from env_config.settings import get_settings
import optparse

if __name__ == '__main__':
    usage = "python start.py -e/--environment <local|prod|dev> "
    parser = optparse.OptionParser(usage)
    parser.add_option('-e', '--environment', dest='env', type='string', help='environment', default='local')
    options, args = parser.parse_args()
    get_settings(options.env)
    from run import start

    start()
