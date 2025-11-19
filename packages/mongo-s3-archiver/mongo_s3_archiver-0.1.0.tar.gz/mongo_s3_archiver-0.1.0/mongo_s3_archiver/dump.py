"""Module implements methods needed to perform dump related operations."""

import os
import sys
import json
import socket
import logging
import datetime
import shutil

from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import Dict, Optional, Union
from hurry.filesize import size, si
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .helpers import env_exists, env_as_bool, env_as_int, normalize_env_value


class MongoBatchPurger:
    """Deletes documents matching provided query in batches."""

    def __init__(self, mongo_uri: str, database: str, collection: str,
                 query_filter: Dict, batch_size: int):
        if batch_size < 1:
            raise ValueError('Batch size must be greater than zero.')
        self.mongo_uri = mongo_uri
        self.database = database
        self.collection = collection
        self.query_filter = query_filter
        self.batch_size = batch_size

    def run(self) -> Dict[str, Union[int, bool, str]]:
        """Executes batched deletion for matched documents."""
        summary: Dict[str, Union[int, bool, str]] = {
            'deleted': 0,
            'batches': 0,
            'success': False
        }
        client: Optional[MongoClient] = None
        try:
            client = MongoClient(self.mongo_uri)
            collection = client[self.database][self.collection]
            while True:
                cursor = collection.find(
                    self.query_filter,
                    projection={'_id': 1},
                    limit=self.batch_size,
                    sort=[('_id', 1)])
                doc_ids = [doc['_id'] for doc in cursor]
                if not doc_ids:
                    break
                delete_result = collection.delete_many({'_id': {'$in': doc_ids}})
                summary['deleted'] += delete_result.deleted_count
                summary['batches'] += 1
                logging.info('Deleted %s documents from "%s.%s" (batch #%s).',
                             delete_result.deleted_count, self.database,
                             self.collection, summary['batches'])
            summary['success'] = True
        except PyMongoError as error_response:
            logging.error('Failed to purge collection "%s.%s": %s',
                          self.database, self.collection, error_response)
            summary['error'] = str(error_response)
        finally:
            if client:
                client.close()
        return summary


class MongoDump:
    """Dumps Mongo database and prepares bson files for the transfer.

    Attributes:
        mongo_uri: connection string in format

        "mongodb://user:password@server:[port]/?replicaSet=NAME&authSource=admin"

        output_folder: path to where local dump will be performed
    """

    def __init__(self):
        """Initializes MongoDump with connection URI."""
        self.mongo_uri = os.getenv('MONGO_URI')

        if not env_exists(self.mongo_uri):
            logging.error(
                'No MongoDB connection URI provided. Nothing to do - exiting now.'
            )
            sys.exit(1)

        mongo_output_folder = os.getenv('MONGO_OUTPUT_FOLDER')

        if not env_exists(mongo_output_folder):
            mongo_output_folder = 'dump'
        self.output_folder = Path(mongo_output_folder).expanduser().resolve()
        self.mongo_db = os.getenv('MONGO_DUMP_DB')
        self.mongo_collection = os.getenv('MONGO_DUMP_COLLECTION')
        self.mongo_query_raw = os.getenv('MONGO_DUMP_QUERY')
        self.mongo_query_document = self._parse_query_filter(self.mongo_query_raw)
        raw_archive_path = os.getenv('MONGO_DUMP_ARCHIVE')
        archive_value = normalize_env_value(raw_archive_path,
                                            strip_inline_comment=True)
        if archive_value:
            archive_path = Path(archive_value).expanduser()
            archive_parent = archive_path.parent
            archive_parent.mkdir(parents=True, exist_ok=True)
            self.archive_path: Optional[Path] = archive_path
        else:
            if env_exists(raw_archive_path):
                logging.warning(
                    'MONGO_DUMP_ARCHIVE was provided but empty after removing inline comments. Ignoring value.'
                )
            self.archive_path = None
        self.parallel_jobs = env_as_int(os.getenv('MONGO_DUMP_JOBS'), 0)
        self.gzip_enabled = env_as_bool(os.getenv('MONGO_DUMP_GZIP'), True)
        self.purge_after_dump = env_as_bool(os.getenv('MONGO_PURGE_AFTER_DUMP'),
                                            False)
        self.purge_batch_size = max(
            1, env_as_int(os.getenv('MONGO_PURGE_BATCH_SIZE'), 1000))

    def _strip_mongo_uri(self) -> list:
        """Strips mongo_uri to get list of mongodb servers provided.

        Returns:
            mongo_srv_list: list, contains tuples in a way (mongo_host:str, *mongo_port:str)
        """
        try:
            mongo_srv_string = (str(self.mongo_uri).split('/'))[2]
        except IndexError:
            mongo_srv_string = str(self.mongo_uri)
        try:
            mongo_srv_string_no_creds = (mongo_srv_string.split('@'))[1]
        except IndexError:
            mongo_srv_string_no_creds = mongo_srv_string
        mongo_srv_list = [
            tuple(location.split(':'))
            for location in mongo_srv_string_no_creds.split(',')
        ]
        return mongo_srv_list

    def _is_srv_uri(self) -> bool:
        """Checks if Mongo URI uses SRV records."""
        return str(self.mongo_uri).lower().startswith('mongodb+srv://')

    @staticmethod
    def _parse_query_filter(query_string: Optional[str]) -> Optional[Dict]:
        """Parses provided JSON query string into dictionary."""
        if not env_exists(query_string):
            return None
        try:
            return json.loads(query_string)
        except json.JSONDecodeError as error_response:
            logging.error('Invalid JSON provided for MONGO_DUMP_QUERY: %s',
                          error_response)
        return None

    def _check_mongo_socket(self) -> bool:
        """Checks if at least one of given servers in mongo_uri is live.

        Returns:
            True: for the first alive server
            False: if none of given servers are live
        """
        if self._is_srv_uri():
            logging.info('Skipping socket availability check for SRV connection string.')
            return True

        for mongo_srv in self._strip_mongo_uri():
            mongo_host = str(mongo_srv[0])
            mongo_port = 27017
            if len(mongo_srv) == 2 and env_exists(mongo_srv[1]):
                try:
                    mongo_port = int(mongo_srv[1])
                except ValueError:
                    logging.warning('Mongo port "%s" is invalid. Using default.',
                                    mongo_srv[1])
            location = (mongo_host, mongo_port)
            with socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM) as mongo_socket:
                try:
                    connection_state = mongo_socket.connect_ex(location)
                    if connection_state == 0:
                        return True
                except socket.gaierror:
                    logging.error('MongoDB is not serving at "%s" port "%s".',
                                 mongo_host, str(mongo_port))
        return False

    def _get_dump_size(self) -> Union[str, bool]:
        """Calculates the size for the dump folder and returns it in SI value.

        Returns:
            folder_size: str, folder size in SI
            'False' in case of failure
        """
        target_path = self.archive_path if self.archive_path else self.output_folder
        target = Path(target_path)
        try:
            if target.is_file():
                summary = target.stat().st_size
            else:
                summary = sum(f.stat().st_size for f in target.rglob('*')
                              if f.is_file())
        except OSError:
            return False
        folder_size = size(summary, system=si)
        logging.info('Dump folder is stored at "%s" and "%s" large.',
                     target, folder_size)
        return folder_size

    def _rename_dump(self) -> Union[str, bool]:
        """Renames temporary dump folder by adding current date.

        Returns:
            folder_name: str, new folder name
        """
        dump_folder_name = f'{str(self.output_folder)}-{str(datetime.date.today())}'
        if Path(dump_folder_name).is_dir():
            logging.warning('Dump folder "%s" already exists. Removing now.',
                            dump_folder_name)
            shutil.rmtree(dump_folder_name)
        try:
            shutil.move(str(self.output_folder), dump_folder_name)
            logging.info('Dump folder renamed and stored at "%s"',
                         dump_folder_name)
        except os.error as error_msg:
            logging.error(error_msg)
            return False
        return dump_folder_name

    def _finalize_dump_destination(self) -> Union[str, bool]:
        """Resolves final dump destination depending on dump mode."""
        if self.archive_path:
            return str(self.archive_path)
        return self._rename_dump()

    @staticmethod
    def _redact_command(command: list) -> list:
        """Masks sensitive values before logging shell command."""
        redacted_args = {'--uri', '--query'}
        result = []
        mask_next = False
        for arg in command:
            if mask_next:
                result.append('<redacted>')
                mask_next = False
                continue
            result.append(arg)
            if arg in redacted_args:
                mask_next = True
        return result

    def dump_db(self) -> bool:
        """Performs dump of the database to the local folder.

        Returns:
            The result of dump command.
            True: if successful
            False: in case of failure
        """
        if not self._check_mongo_socket():
            return False

        command = ['mongodump', '--uri', self.mongo_uri]

        if env_exists(self.mongo_db):
            command.extend(['--db', self.mongo_db])
        if env_exists(self.mongo_collection):
            command.extend(['--collection', self.mongo_collection])
        if env_exists(self.mongo_query_raw):
            command.extend(['--query', self.mongo_query_raw])
        if self.parallel_jobs > 0:
            command.extend(['-j', str(self.parallel_jobs)])
        if self.archive_path:
            command.extend(['--archive', str(self.archive_path)])
        else:
            self.output_folder.mkdir(parents=True, exist_ok=True)
            command.extend(['--out', str(self.output_folder)])
        if self.gzip_enabled:
            command.append('--gzip')

        logging.info('Executing mongodump command: %s',
                     ' '.join(self._redact_command(command)))

        try:
            dump_process = Popen(command, stdout=PIPE, stderr=STDOUT)
        except FileNotFoundError:
            logging.error(
                '"mongodump" command is not available in PATH. Please install MongoDB Database Tools.'
            )
            return False

        if dump_process.stdout:
            with dump_process.stdout:
                for line in iter(dump_process.stdout.readline, b''):
                    dump_process_output = line.decode('utf-8').strip('\n')
                    if dump_process_output:
                        logging.info(dump_process_output)

        exit_code = dump_process.wait()
        if exit_code == 0:
            return True
        logging.error('mongodump command exited with status "%s".', exit_code)
        return False

    def cleanup(self) -> bool:
        """Performs cleanup steps on exist or failure.

        Returns:
            True: if successful
            False: in case of failure
        """
        try:
            if self.archive_path:
                archive_path = Path(self.archive_path)
                if archive_path.is_file():
                    logging.warning('Performing cleanup steps - "%s" removed.',
                                    archive_path)
                    archive_path.unlink()
                return True

            dump_folder_name = Path(
                f'{str(self.output_folder)}-{str(datetime.date.today())}')
            if dump_folder_name.is_dir():
                logging.warning('Performing cleanup steps - "%s" removed.',
                                dump_folder_name)
                shutil.rmtree(dump_folder_name)
            if self.output_folder.is_dir():
                logging.warning('Performing cleanup steps - "%s" removed.',
                                self.output_folder)
                shutil.rmtree(self.output_folder)
            return True
        except OSError:
            logging.error('Application failed to perform cleanup steps')
            return False

    def exec(self) -> dict:
        """Wraps all class methods for single start

        Returns:
            result: dict, result of dump operations as dictionary
        """
        dump_state = self.dump_db()
        if dump_state:
            dump_path = self._finalize_dump_destination()
            if dump_path:
                result = {
                    'dump': str(dump_state),
                    'size': self._get_dump_size(),
                    'path': dump_path
                }
            else:
                result = {'dump': 'False'}
        else:
            result = {'dump': str(dump_state)}
        logging.debug(str(result))
        return result

    def purge_backed_documents(self) -> Optional[Dict[str, Union[int, bool, str]]]:
        """Deletes documents that were backed up if feature is enabled."""
        if not self.purge_after_dump:
            return None
        if not (env_exists(self.mongo_db) and env_exists(self.mongo_collection)):
            logging.error(
                'Purge after dump requested but MONGO_DUMP_DB '
                'and MONGO_DUMP_COLLECTION are not configured.')
            return None
        if not self.mongo_query_document:
            logging.error('Purge after dump requested but MONGO_DUMP_QUERY is missing or invalid JSON.')
            return None

        try:
            purger = MongoBatchPurger(self.mongo_uri, self.mongo_db,
                                      self.mongo_collection,
                                      self.mongo_query_document,
                                      self.purge_batch_size)
        except ValueError as error_response:
            logging.error(error_response)
            return None

        summary = purger.run()
        if summary.get('success'):
            logging.info(
                'Purge completed: %s documents deleted from "%s.%s" in %s batches.',
                summary['deleted'], self.mongo_db, self.mongo_collection,
                summary['batches'])
        return summary
