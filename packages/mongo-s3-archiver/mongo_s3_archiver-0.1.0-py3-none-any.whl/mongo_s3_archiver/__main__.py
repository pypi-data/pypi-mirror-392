"""Main module contains functions needed by mongo-s3-archiver package."""

import os
import sys
import argparse
import logging

from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from mongo_s3_archiver import S3
from mongo_s3_archiver import MongoDump
from mongo_s3_archiver import Notifications
from mongo_s3_archiver import __version__

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class MongoDumpS3:
    """Implement CLI and handles command execution.

    Attributes:
        options: startup options passed to the application
    """

    def __init__(self):
        """Initializes MongoDumpS3 with startup options."""
        self.options = self._startup_options()
        self.exec()

    @staticmethod
    def _startup_options() -> argparse.Namespace:
        """Function implements CLI interface.

        Returns:
            argparse.Namespace: object that contains all passed flags
        """

        cli_parser = argparse.ArgumentParser(
            prog='mongo-s3-archiver',
            usage='%(prog)s <options>',
            description='Export the content of a running server into .bson files'
            ' and uploads to provided S3 compatible storage.'
            ' By default loads required settings from environment'
            ' variables.',
            epilog='Email bug reports, questions, discussions'
            ' to mailto:123.hadikoubeissy@gmail.com.'
            ' Please star project on GitHub:'
            ' https://github.com/hadikoub/mongo-s3-archiver',
            add_help=False)

        # Section: general options
        general = cli_parser.add_argument_group('general options')
        general.add_argument('-h',
                             '--help',
                             action='help',
                             default=argparse.SUPPRESS,
                             help='print usage')

        general.add_argument('-v',
                             '--version',
                             action='version',
                             version=f'%(prog)s {__version__}',
                             help='print the tool version and exit')

        # Section: output options
        output = cli_parser.add_argument_group('output options')
        output.add_argument(
            '-b',
            '--bucket',
            action='store',
            metavar='<S3 Bucket>',
            help='S3 bucket name for upload, defaults to \'mongodump\'')
        output.add_argument('-o',
                            '--out',
                            action='store',
                            metavar='<folder>',
                            help='output directory, defaults to \'dump\'')

        # Section: uri options
        uri = cli_parser.add_argument_group('uri options')
        uri.add_argument(
            '-u',
            '--uri',
            action='store',
            type=str,
            metavar='<uri>',
            help='mongodb uri connection string.'
            ' See official description here'
            ' https://docs.mongodb.com/manual/reference/connection-string')

        # Section: dump selection options
        dump_selection = cli_parser.add_argument_group(
            'dump selection options')
        dump_selection.add_argument(
            '-d',
            '--db',
            action='store',
            type=str,
            metavar='<database>',
            help='Optional MongoDB database to dump. Required when using collection scoped dumps.'
        )
        dump_selection.add_argument(
            '-c',
            '--collection',
            action='store',
            type=str,
            metavar='<collection>',
            help='Optional MongoDB collection to dump.')
        dump_selection.add_argument(
            '-q',
            '--query',
            action='store',
            type=str,
            metavar='<query>',
            help='Optional MongoDB query in JSON format that narrows the dump scope.'
        )

        # Section: dump performance options
        dump_tuning = cli_parser.add_argument_group(
            'dump performance options')
        dump_tuning.add_argument(
            '--archive',
            action='store',
            type=str,
            metavar='<archive-file>',
            help='Write dump into a single archive file instead of folder.')
        dump_tuning.add_argument(
            '-j',
            '--jobs',
            action='store',
            type=int,
            metavar='<workers>',
            help='Number of concurrent collections for mongodump.')
        dump_tuning.add_argument(
            '--no-gzip',
            action='store_true',
            help='Disable gzip compression when running mongodump.')

        # Section: post processing options
        post_dump = cli_parser.add_argument_group('post processing options')
        post_dump.add_argument(
            '--delete-after-dump',
            action='store_true',
            help='Delete documents that match the query once the dump is uploaded.'
        )
        post_dump.add_argument(
            '--delete-batch-size',
            action='store',
            type=int,
            metavar='<batch-size>',
            help='Number of documents to delete per batch when --delete-after-dump is enabled.'
        )

        # Section: environmental options
        env = cli_parser.add_argument_group('environmental options')
        env.add_argument('-e',
                         '--env',
                         action='store',
                         type=str,
                         metavar='<env-file>',
                         help='path to file containing environmental variables')

        # Section: cloud storage options
        cloud_storage = cli_parser.add_argument_group('cloud storage options')
        cloud_storage.add_argument(
            '--azure',
            action='store',
            type=str,
            metavar='"<azure_storage_connection_string>"',
            help='connection string for storage account provided by Azure')

        cloud_storage.add_argument(
            '--aws',
            action='store',
            type=str,
            metavar='"<aws_access_key_id=value>'
            ' <aws_secret_access_key=value> <aws_region=value>"',
            help='AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION properties'
            ' provided by Amazon Web Services IAM. '
            'AWS_REGION defaults to \'us-west-2\' if not specified')
        cloud_storage.add_argument(
            '--gcp',
            action='store',
            type=str,
            metavar=
            '"<google_application_credentials=value> <google_region=value>"',
            help='path to service account file and optional Google Cloud Region.'
            ' GOOGLE_REGION defaults to \'us-multiregion\' if not specified')

        # Section: notification options
        notification = cli_parser.add_argument_group('notification options')
        notification.add_argument(
            '--email',
            action='store',
            metavar='<user@example.com>',
            help='email address which to notify upon the result')
        notification.add_argument(
            '--smtp',
            action='store',
            metavar='<mail-server.example.com>',
            help='SMTP relay server to use, defaults to \'localhost\'')
        notification.add_argument(
            '--telegram',
            action='store',
            type=str,
            metavar='"<telegram_token=value> <telegram_chat_id=value>"',
            help='Telegram API token and chat id to be used for notification. '
            ' See more: https://core.telegram.org/bots/api')

        return cli_parser.parse_args()

    @staticmethod
    def mask_env(scope: str = 'all') -> bool:
        """Masks environment variables when flags passed.

        Returns:
            True: if successful
            False: in case of failure
        """
        if scope == 'cloud':
            cloud_env_vars = [
                'AZURE_STORAGE_CONNECTION_STRING',
                'AWS_REGION',
                'AWS_ACCESS_KEY_ID',
                'AWS_SECRET_ACCESS_KEY',
                'GOOGLE_APPLICATION_CREDENTIALS',
                'GOOGLE_REGION',
            ]
        else:
            cloud_env_vars = [
                'MONGO_URI',
                'MONGO_OUTPUT_FOLDER',
                'MONGO_DUMP_BUCKET',
                'MONGO_DUMP_DB',
                'MONGO_DUMP_COLLECTION',
                'MONGO_DUMP_QUERY',
                'MONGO_DUMP_ARCHIVE',
                'MONGO_DUMP_JOBS',
                'MONGO_DUMP_GZIP',
                'MONGO_PURGE_AFTER_DUMP',
                'MONGO_PURGE_BATCH_SIZE',
                'EMAIL',
                'SMTP_RELAY',
                'TELEGRAM_TOKEN',
                'TELEGRAM_CHAT_ID',
                'AZURE_STORAGE_CONNECTION_STRING',
                'AWS_REGION',
                'AWS_ACCESS_KEY_ID',
                'AWS_SECRET_ACCESS_KEY',
                'GOOGLE_APPLICATION_CREDENTIALS',
                'GOOGLE_REGION',
            ]
        try:
            for env in cloud_env_vars:
                os.unsetenv(env)
            return True
        except OSError as error_response:
            logging.error(error_response)
        return False

    @staticmethod
    def _str_to_dict(argument_string: str) -> dict:
        """Converts passed long key-value argument to python dictionary.

        Returns:
            result: dict, containing passed options
        """
        result = {}
        separate_kv = argument_string.split(' ')
        for flags in separate_kv:
            flag_key, flag_value = flags.split('=')
            result[flag_key] = flag_value
        return result

    @staticmethod
    def _set_env(env_kwargs: dict) -> bool:
        """Sets environment variables from passed dictionary.

        Returns:
            True: if successful
            False: in case of failure
        """
        try:
            for key in env_kwargs:
                os.environ[str(key).upper()] = str(env_kwargs[key])
        except OSError as error_response:
            logging.error(error_response)
            logging.error('Application was not able to set env variables.'
                          ' Please report the bug to mailto:hi@exesse.org')
            return False
        return True

    @staticmethod
    def debug_env() -> None:
        """Helper method that prints all possible env vars."""
        logging.debug('MONGO_URI set to "%s"', os.getenv('MONGO_URI'))
        logging.debug('MONGO_OUTPUT_FOLDER set to "%s"',
                      os.getenv('MONGO_OUTPUT_FOLDER'))
        logging.debug('MONGO_DUMP_BUCKET set to "%s"',
                      os.getenv('MONGO_DUMP_BUCKET'))
        logging.debug('MONGO_DUMP_DB set to "%s"', os.getenv('MONGO_DUMP_DB'))
        logging.debug('MONGO_DUMP_COLLECTION set to "%s"',
                      os.getenv('MONGO_DUMP_COLLECTION'))
        logging.debug('MONGO_DUMP_QUERY set to "%s"',
                      os.getenv('MONGO_DUMP_QUERY'))
        logging.debug('MONGO_DUMP_ARCHIVE set to "%s"',
                      os.getenv('MONGO_DUMP_ARCHIVE'))
        logging.debug('MONGO_DUMP_JOBS set to "%s"',
                      os.getenv('MONGO_DUMP_JOBS'))
        logging.debug('MONGO_DUMP_GZIP set to "%s"',
                      os.getenv('MONGO_DUMP_GZIP'))
        logging.debug('EMAIL set to "%s"', os.getenv('EMAIL'))
        logging.debug('SMTP_RELAY set to "%s"', os.getenv('SMTP_RELAY'))
        logging.debug('TELEGRAM_TOKEN set to "%s"', os.getenv('TELEGRAM_TOKEN'))
        logging.debug('TELEGRAM_CHAT_ID set to "%s"',
                      os.getenv('TELEGRAM_CHAT_ID'))
        logging.debug('MONGO_PURGE_AFTER_DUMP set to "%s"',
                      os.getenv('MONGO_PURGE_AFTER_DUMP'))
        logging.debug('MONGO_PURGE_BATCH_SIZE set to "%s"',
                      os.getenv('MONGO_PURGE_BATCH_SIZE'))
        logging.debug('AZURE_STORAGE_CONNECTION_STRING set to "%s"',
                      os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
        logging.debug('AWS_REGION set to "%s"', os.getenv('AWS_REGION'))
        logging.debug('AWS_ACCESS_KEY_ID set to "%s"',
                      os.getenv('AWS_ACCESS_KEY_ID'))
        logging.debug('AWS_SECRET_ACCESS_KEY set to "%s"',
                      os.getenv('AWS_SECRET_ACCESS_KEY'))
        logging.debug('GOOGLE_APPLICATION_CREDENTIALS set to "%s"',
                      os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
        logging.debug('GOOGLE_REGION set to "%s"', os.getenv('GOOGLE_REGION'))

    def _check_env_file(self) -> bool:
        """Checks if env-file was passed and clears env if True.

        Returns:
            True: if successful
            False: in case of failure
        """
        if self.options.env:
            env_file_path = Path(self.options.env)
            if env_file_path.is_file():
                load_dotenv(dotenv_path=env_file_path)
                self.debug_env()
                return True
            logging.error(
                'Provided env file "%s" does not exists. Please check.',
                self.options.env)

        return False

    def _check_output_flags(self) -> bool:
        """Checks for passed output related startup flags.

        Returns:
            True: if successful
            False: in case of failure
        """
        if self.options.bucket or self.options.out:
            bucket = {'MONGO_DUMP_BUCKET': self.options.bucket}
            out = {'MONGO_OUTPUT_FOLDER': self.options.out}

            if not self._set_env(bucket):
                logging.error('Failed to set variable "%s"', bucket)
                return False
            if not self._set_env(out):
                logging.error('Failed to set variable "%s"', out)
                return False

            return True

        return False

    def _check_dump_selection_flags(self) -> bool:
        """Checks for dump selection related flags."""
        dump_flags = {}
        if self.options.db:
            dump_flags['MONGO_DUMP_DB'] = self.options.db
        if self.options.collection:
            dump_flags['MONGO_DUMP_COLLECTION'] = self.options.collection
        if self.options.query:
            dump_flags['MONGO_DUMP_QUERY'] = self.options.query
        if not dump_flags:
            return False
        if not self._set_env(dump_flags):
            logging.error('Failed to set dump selection variables "%s".',
                          dump_flags)
            return False
        return True

    def _check_dump_tuning_flags(self) -> bool:
        """Checks for dump tuning related flags."""
        tuning_flags = {}
        if self.options.archive:
            tuning_flags['MONGO_DUMP_ARCHIVE'] = self.options.archive
        if self.options.jobs:
            tuning_flags['MONGO_DUMP_JOBS'] = self.options.jobs
        if self.options.no_gzip:
            tuning_flags['MONGO_DUMP_GZIP'] = 'false'
        if not tuning_flags:
            return False
        if not self._set_env(tuning_flags):
            logging.error('Failed to set dump tuning variables "%s".',
                          tuning_flags)
            return False
        return True

    def _check_post_dump_flags(self) -> bool:
        """Checks for post dump related flags."""
        post_flags = {}
        if self.options.delete_after_dump:
            post_flags['MONGO_PURGE_AFTER_DUMP'] = 'true'
        if self.options.delete_batch_size:
            post_flags['MONGO_PURGE_BATCH_SIZE'] = self.options.delete_batch_size
        if not post_flags:
            return False
        if not self._set_env(post_flags):
            logging.error('Failed to set post dump variables "%s".',
                          post_flags)
            return False
        return True

    def _check_cloud_flags(self) -> bool:
        """Checks for S3 cloud specific flags.

        Returns:
            True: if successful
            False: in case of failure
        """
        if self.options.azure or self.options.aws or self.options.gcp:
            if self.mask_env('cloud'):

                if self.options.azure:
                    azure = {
                        'AZURE_STORAGE_CONNECTION_STRING': self.options.azure
                    }
                    if not self._set_env(azure):
                        logging.error('Failed to set variable "%s"', azure)
                        return False
                if self.options.gcp:
                    gcp = self._str_to_dict(self.options.gcp)
                    if not self._set_env(gcp):
                        logging.error('Failed to set variable "%s"', gcp)
                        return False
                if self.options.aws:
                    aws = self._str_to_dict(self.options.aws)
                    if not self._set_env(aws):
                        logging.error('Failed to set variable "%s"', aws)
                        return False

                return True

        return False

    def _check_notifications_flags(self) -> bool:
        """Checks for passed notification related startup flags.

        Returns:
            True: if successful
            False: in case of failure
        """
        if not (self.options.email or self.options.smtp
                or self.options.telegram):
            return False

        if self.options.email:
            email = {'EMAIL': self.options.email}
            if not self._set_env(email):
                logging.error('Failed to set variable "%s"', email)
                return False

        if self.options.smtp:
            smtp = {'SMTP_RELAY': self.options.smtp}
            if not self._set_env(smtp):
                logging.error('Failed to set variable "%s"', smtp)
                return False

        if self.options.telegram:
            telegram = self._str_to_dict(self.options.telegram)
            if not self._set_env(telegram):
                logging.error('Failed to set variable "%s"', telegram)
                return False

        return True

    def _prepare_app_env(self) -> bool:
        """Prepares working environment.

        Returns:
            True: if successful
            False: in case of failure
        """
        if self._check_env_file():
            logging.info('App properties were provided with env file.')
            return True
        if self.options.uri:
            uri = {'MONGO_URI': self.options.uri}
            logging.info('MongoDB uri was passed as startup flag.')
            if not self._set_env(uri):
                return False
        if self._check_output_flags():
            logging.info('Output properties were provided with startup flags.'
                         ' Masking related env vars now.')
        if self._check_dump_selection_flags():
            logging.info(
                'Dump selection properties were provided with startup flags.')
        if self._check_dump_tuning_flags():
            logging.info('Dump tuning properties were provided with startup flags.'
                         ' Masking related env vars now.')
        if self._check_cloud_flags():
            logging.info(
                'S3 connection properties were provided with startup flags.'
                ' Masking related env vars now.')
        if self._check_post_dump_flags():
            logging.info(
                'Post dump properties were provided with startup flags.'
                ' Masking related env vars now.')
        if self._check_notifications_flags():
            logging.info(
                'Notification properties were provided with startup flags.'
                ' Masking related env vars now.')
        self.debug_env()
        return True

    def exec(self) -> bool:
        """Helper function that executes class MongoDUmpS3.

        Returns:
            True: if successful
            False: in case of failure
        """
        start = datetime.now()
        if self._prepare_app_env():
            failure = '\U0001F4A9 mongo-s3-archiver failed. Please see logs.'
            mongodump = MongoDump()
            dump_result = mongodump.exec()

            if dump_result['dump'] == 'False':
                Notifications(failure)
                mongodump.cleanup()
                return False

            dump_size = dump_result['size']
            dump_path = dump_result['path']
            dump_path_object = Path(dump_path)
            dump_path_parent = str(dump_path_object.parent)

            s3_upload = S3()
            if dump_path_object.is_file():
                s3_upload_result = s3_upload.upload_local_file(
                    str(dump_path_object), dump_path_object.name)
            else:
                s3_upload_result = s3_upload.upload_local_folder(
                    str(dump_path_object), dump_path_parent)

            if s3_upload_result:
                end = str(datetime.now() - start)[:-7]
                purge_note = ''
                purge_result = mongodump.purge_backed_documents()
                if purge_result:
                    if purge_result.get('success'):
                        purge_note = '\n\U0001F9F9 Deleted %(deleted)s documents in %(batches)s batches.' % (
                            {
                                'deleted': purge_result.get('deleted', 0),
                                'batches': purge_result.get('batches', 0)
                            })
                    else:
                        purge_note = '\n\U000026A0 Document purge requested but failed. Please check logs.'
                success = '\U0001F4A5 mongo-s3-archiver finished the job.' \
                          '\n\U0001F9BA Dump size is %s.' \
                          '\n\U0001F312 Processing time is %s%s' % (dump_size, end, purge_note)
                Notifications(success)
                mongodump.cleanup()
                return True
            mongodump.cleanup()
        return False


def main():
    """Wraps complete package to end-user."""
    run_app = MongoDumpS3()
    if run_app:
        sys.exit(0)
    sys.exit(1)


if __name__ == '__main__':
    main()
