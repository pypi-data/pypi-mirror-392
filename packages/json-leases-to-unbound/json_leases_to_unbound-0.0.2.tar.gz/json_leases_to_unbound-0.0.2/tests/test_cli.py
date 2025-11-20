import pytest
from unittest.mock import patch, MagicMock
from json_leases_to_unbound import cli


class TestCLI:
    """Tests for CLI argument parsing and execution."""
    
    def test_main_cli_default_arguments(self, mocker):
        """Test CLI with default arguments."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = ['json-leases-to-unbound']
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        mock_main.assert_called_once()
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['log_level'] == 'INFO'
        assert call_kwargs['source'] == '/run/slaac-resolver/'
        assert call_kwargs['domain'] == 'lan'
        assert call_kwargs['unbound_server'] is None
        assert call_kwargs['config_file'] is None
    
    def test_main_cli_custom_log_level(self, mocker):
        """Test CLI with custom log level."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = ['json-leases-to-unbound', '--log-level', 'DEBUG']
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['log_level'] == 'DEBUG'
    
    def test_main_cli_custom_source(self, mocker):
        """Test CLI with custom source directory."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = ['json-leases-to-unbound', '--source', '/tmp/leases']
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['source'] == '/tmp/leases'
    
    def test_main_cli_custom_domain(self, mocker):
        """Test CLI with custom domain."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = ['json-leases-to-unbound', '--domain', 'home.local']
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['domain'] == 'home.local'
    
    def test_main_cli_with_unbound_server(self, mocker):
        """Test CLI with unbound server specification."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = ['json-leases-to-unbound', '--unbound-server', '192.168.1.1:8953']
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['unbound_server'] == '192.168.1.1:8953'
    
    def test_main_cli_with_config_file(self, mocker):
        """Test CLI with config file path."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = ['json-leases-to-unbound', '--config-file', '/etc/unbound/unbound.conf']
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['config_file'] == '/etc/unbound/unbound.conf'
    
    def test_main_cli_all_arguments(self, mocker):
        """Test CLI with all arguments specified."""
        mock_main = mocker.patch('json_leases_to_unbound.main')
        mock_argv = [
            'json-leases-to-unbound',
            '--log-level', 'WARNING',
            '--source', '/custom/path',
            '--domain', 'custom.local',
            '--unbound-server', '10.0.0.1:8953',
            '--config-file', '/custom/unbound.conf'
        ]
        
        with patch('sys.argv', mock_argv):
            cli.main_cli()
        
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs['log_level'] == 'WARNING'
        assert call_kwargs['source'] == '/custom/path'
        assert call_kwargs['domain'] == 'custom.local'
        assert call_kwargs['unbound_server'] == '10.0.0.1:8953'
        assert call_kwargs['config_file'] == '/custom/unbound.conf'
    
    def test_main_cli_invalid_log_level(self, capsys):
        """Test CLI with invalid log level."""
        mock_argv = ['json-leases-to-unbound', '--log-level', 'INVALID']
        
        with patch('sys.argv', mock_argv):
            with pytest.raises(SystemExit):
                cli.main_cli()
        
        captured = capsys.readouterr()
        assert "invalid choice" in captured.err.lower()
