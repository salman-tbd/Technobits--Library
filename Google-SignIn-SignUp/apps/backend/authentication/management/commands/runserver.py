"""
Custom runserver command that defaults to port 8003
"""
from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings


class Command(RunserverCommand):
    """Custom runserver command with default port 8003"""
    
    default_addr = '127.0.0.1'
    default_port = '8003'
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        # Override the default port
        parser.set_defaults(addrport='127.0.0.1:8003')
    
    def handle(self, *args, **options):
        # If no addrport is provided, set our default
        if not options.get('addrport'):
            options['addrport'] = '127.0.0.1:8003'
        
        # Call the parent runserver command
        super().handle(*args, **options)
