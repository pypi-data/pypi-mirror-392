import pytest
import json
import ipaddress
import os
from unittest.mock import Mock, patch, MagicMock
from json_leases_to_unbound import core


class TestLeaseExtraction:
    """Tests for lease data extraction and filtering."""
    
    def test_extract_leases_valid_data(self):
        """Test extracting leases from valid JSON data."""
        data = [
            {
                "Address": [0x2001, 0xdb8, 0, 0, 0, 0, 0, 1],
                "AddressType": "IPv6",
                "Hostname": "test-host",
                "Expire": "2025-12-31T23:59:59Z"
            }
        ]
        
        leases = core.extract_leases(data)
        
        assert len(leases) == 1
        assert leases[0]["hostname"] == "test-host"
        # Note: hex 0x2001 = 8193, 0xdb8 = 3512 in decimal
        assert leases[0]["address"] == ipaddress.ip_address("8193:3512::1")
        assert leases[0]["expire"] == "2025-12-31T23:59:59Z"
    
    def test_extract_leases_missing_hostname(self):
        """Test extracting leases when hostname is missing."""
        data = [
            {
                "Address": [0x2001, 0xdb8, 0, 0, 0, 0, 0, 1],
                "AddressType": "IPv6",
                "Expire": "2025-12-31T23:59:59Z"
            }
        ]
        
        leases = core.extract_leases(data)
        
        assert len(leases) == 1
        assert leases[0]["hostname"] == ""
    
    def test_filter_leases_by_expiration_keeps_latest(self):
        """Test that filtering keeps the lease with the latest expiration."""
        leases = [
            {
                "hostname": "test-host",
                "address": ipaddress.ip_address("2001:db8::1"),
                "expire": "2025-12-30T23:59:59Z"
            },
            {
                "hostname": "test-host",
                "address": ipaddress.ip_address("2001:db8::2"),
                "expire": "2025-12-31T23:59:59Z"
            }
        ]
        
        filtered = core.filter_leases_by_expiration(leases)
        
        assert len(filtered) == 1
        assert filtered[0]["address"] == ipaddress.ip_address("2001:db8::2")
        assert filtered[0]["expire"] == "2025-12-31T23:59:59Z"
    
    def test_filter_leases_by_expiration_multiple_hostnames(self):
        """Test filtering with multiple different hostnames."""
        leases = [
            {
                "hostname": "host1",
                "address": ipaddress.ip_address("2001:db8::1"),
                "expire": "2025-12-31T23:59:59Z"
            },
            {
                "hostname": "host2",
                "address": ipaddress.ip_address("2001:db8::2"),
                "expire": "2025-12-31T23:59:59Z"
            }
        ]
        
        filtered = core.filter_leases_by_expiration(leases)
        
        assert len(filtered) == 2


class TestDNSRecordGeneration:
    """Tests for DNS record generation functions."""
    
    def test_add_to_unbound(self):
        """Test generating DNS records for adding a lease."""
        core.default_domain = "lan"
        hostname = "test-host"
        address = ipaddress.ip_address("2001:db8::1")
        
        records = core.add_to_unbound(hostname, address)
        
        assert len(records) == 2
        assert "test-host.lan" in records[1]
        assert "IN AAAA 2001:db8::1" in records[1]
        assert "PTR test-host.lan" in records[0]
    
    def test_remove_from_unbound(self):
        """Test generating DNS records for removing a lease."""
        core.default_domain = "lan"
        hostname = "test-host"
        address = ipaddress.ip_address("2001:db8::1")
        
        records = core.remove_from_unbound(hostname, address)
        
        assert len(records) == 2
        assert "test-host.lan" in records[1]
        assert "IN AAAA 2001:db8::1" in records[1]
    
    def test_modify_on_unbound(self):
        """Test generating DNS records for modifying a lease."""
        core.default_domain = "lan"
        hostname = "test-host"
        new_address = ipaddress.ip_address("2001:db8::2")
        old_address = ipaddress.ip_address("2001:db8::1")
        
        add_rr, remove_rr = core.modify_on_unbound(hostname, new_address, old_address)
        
        assert len(add_rr) == 2
        assert len(remove_rr) == 2
        assert "2001:db8::2" in add_rr[1]
        assert "2001:db8::1" in remove_rr[1]


class TestUnboundControl:
    """Tests for unbound-control interactions."""
    
    def test_find_unbound_control_with_which(self, mocker):
        """Test finding unbound-control using which command."""
        core.UNBOUND_CONTROL_PATH = None
        mocker.patch('shutil.which', return_value='/usr/sbin/unbound-control')
        
        path = core.find_unbound_control()
        
        assert path == '/usr/sbin/unbound-control'
    
    def test_find_unbound_control_fallback(self, mocker):
        """Test finding unbound-control using fallback paths."""
        core.UNBOUND_CONTROL_PATH = None
        mocker.patch('shutil.which', return_value=None)
        mocker.patch('os.path.isfile', side_effect=lambda p: p == '/usr/sbin/unbound-control')
        mocker.patch('os.access', return_value=True)
        
        path = core.find_unbound_control()
        
        assert path == '/usr/sbin/unbound-control'
    
    def test_find_unbound_control_not_found(self, mocker):
        """Test exception when unbound-control is not found."""
        core.UNBOUND_CONTROL_PATH = None
        mocker.patch('shutil.which', return_value=None)
        mocker.patch('os.path.isfile', return_value=False)
        
        with pytest.raises(FileNotFoundError):
            core.find_unbound_control()
    
    def test_unbound_control_with_server_and_config(self, mock_unbound_control, tmp_path):
        """Test unbound_control with server and config file parameters."""
        mock_run, mock_which = mock_unbound_control
        
        # Create a temporary config file since code checks if it exists
        config_file = tmp_path / "unbound.conf"
        config_file.write_text("# test config")
        
        core.unbound_control(['status'], server='127.0.0.1:8953', config_file=str(config_file))
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert '-c' in call_args
        assert str(config_file) in call_args
        assert '-s' in call_args
        assert '127.0.0.1:8953' in call_args
        assert 'status' in call_args
    
    def test_apply_unbound_changes_with_additions(self, mock_unbound_control):
        """Test applying DNS record additions to Unbound."""
        mock_run, _ = mock_unbound_control
        
        add_rr = ["test-host.lan IN AAAA 2001:db8::1"]
        core.apply_unbound_changes(True, [], add_rr)
        
        assert mock_run.call_count == 1
        call_args = mock_run.call_args[0][0]
        assert 'local_datas' in call_args
    
    def test_apply_unbound_changes_with_removals(self, mock_unbound_control):
        """Test applying DNS record removals to Unbound."""
        mock_run, _ = mock_unbound_control
        
        remove_rr = ["test-host.lan IN AAAA 2001:db8::1"]
        core.apply_unbound_changes(True, remove_rr, [])
        
        assert mock_run.call_count == 1
        call_args = mock_run.call_args[0][0]
        assert 'local_datas_remove' in call_args


class TestLeaseFileProcessing:
    """Tests for lease file reading and processing."""
    
    def test_read_file_valid(self, sample_lease_file):
        """Test reading a valid lease file."""
        leases = core.read_file(sample_lease_file)
        
        assert len(leases) == 2
        assert leases[0]["hostname"] in ["test-host", "another-host"]
    
    def test_read_file_not_found(self, caplog):
        """Test reading a non-existent file."""
        leases = core.read_file("/nonexistent/file.json")
        
        assert len(leases) == 0
        assert "Error reading file" in caplog.text
    
    def test_read_file_invalid_json(self, temp_lease_dir, caplog):
        """Test reading a file with invalid JSON."""
        invalid_file = os.path.join(temp_lease_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("not valid json{")
        
        leases = core.read_file(invalid_file)
        
        assert len(leases) == 0
        assert "Error reading file" in caplog.text
    
    def test_process_lease_file_new_leases(self, sample_lease_file, mock_unbound_control):
        """Test processing a lease file with new leases."""
        core.active_leases = {}
        core.default_domain = "lan"
        mock_run, _ = mock_unbound_control
        
        result = core.process_lease_file(sample_lease_file)
        
        filename = os.path.basename(sample_lease_file)
        assert filename in result
        assert len(result[filename]) == 2
        assert mock_run.call_count == 1
    
    def test_process_lease_file_modified_lease(self, temp_lease_dir, mock_unbound_control):
        """Test processing a lease file with a modified address."""
        core.active_leases = {}
        core.default_domain = "lan"
        mock_run, _ = mock_unbound_control
        
        # Initial lease
        lease_file = os.path.join(temp_lease_dir, "test.json")
        data = [{
            "Address": [0x2001, 0xdb8, 0, 0, 0, 0, 0, 1],
            "AddressType": "IPv6",
            "Hostname": "test-host",
            "Expire": "2025-12-31T23:59:59Z"
        }]
        with open(lease_file, 'w') as f:
            json.dump(data, f)
        
        core.process_lease_file(lease_file)
        mock_run.reset_mock()
        
        # Modified lease
        data[0]["Address"] = [0x2001, 0xdb8, 0, 0, 0, 0, 0, 2]
        with open(lease_file, 'w') as f:
            json.dump(data, f)
        
        core.process_lease_file(lease_file)
        
        # Should have both add and remove operations
        assert mock_run.call_count == 2


class TestInitialRun:
    """Tests for initial run functionality."""
    
    def test_initial_run_single_file(self, sample_lease_file, mock_unbound_control):
        """Test initial run with a single file."""
        core.active_leases = {}
        core.default_domain = "lan"
        
        core.initial_run(sample_lease_file)
        
        assert len(core.active_leases) == 1
    
    def test_initial_run_directory(self, temp_lease_dir, sample_lease_data, mock_unbound_control):
        """Test initial run with a directory."""
        core.active_leases = {}
        core.default_domain = "lan"
        
        # Create multiple lease files
        for i in range(3):
            lease_file = os.path.join(temp_lease_dir, f"lease-{i}.json")
            with open(lease_file, 'w') as f:
                json.dump(sample_lease_data, f)
        
        core.initial_run(temp_lease_dir)
        
        assert len(core.active_leases) == 3
    
    def test_initial_run_nonexistent_source(self, caplog):
        """Test initial run with non-existent source."""
        with pytest.raises(SystemExit):
            core.initial_run("/nonexistent/path")


class TestDirChangeHandler:
    """Tests for directory change handler."""
    
    def test_handler_initialization(self, temp_lease_dir):
        """Test DirChangeHandler initialization."""
        handler = core.DirChangeHandler(temp_lease_dir)
        
        assert handler.source_dir == temp_lease_dir
    
    def test_handler_on_created_event(self, temp_lease_dir, mock_unbound_control, mocker):
        """Test handler response to file creation."""
        core.active_leases = {}
        core.default_domain = "lan"
        
        handler = core.DirChangeHandler(temp_lease_dir)
        
        # Create mock event
        event = Mock()
        event.event_type = "created"
        event.is_directory = False
        event.src_path = os.path.join(temp_lease_dir, "new-lease.json")
        
        # Create the actual file
        data = [{
            "Address": [0x2001, 0xdb8, 0, 0, 0, 0, 0, 1],
            "AddressType": "IPv6",
            "Hostname": "new-host",
            "Expire": "2025-12-31T23:59:59Z"
        }]
        with open(event.src_path, 'w') as f:
            json.dump(data, f)
        
        handler.on_any_event(event)
        
        assert "new-lease.json" in core.active_leases
    
    def test_handler_on_deleted_event(self, sample_lease_file, mock_unbound_control):
        """Test handler response to file deletion."""
        core.active_leases = {}
        core.default_domain = "lan"
        mock_run, _ = mock_unbound_control
        
        # First process the file
        core.process_lease_file(sample_lease_file)
        filename = os.path.basename(sample_lease_file)
        assert filename in core.active_leases
        
        # Mock deletion event
        handler = core.DirChangeHandler(os.path.dirname(sample_lease_file))
        event = Mock()
        event.event_type = "deleted"
        event.src_path = sample_lease_file
        
        handler.on_any_event(event)
        
        assert filename not in core.active_leases


class TestMainFunction:
    """Tests for the main entry point."""
    
    def test_main_with_valid_parameters(self, temp_lease_dir, sample_lease_data, mock_unbound_control, mocker):
        """Test main function with valid parameters."""
        # Create a lease file
        lease_file = os.path.join(temp_lease_dir, "test.json")
        with open(lease_file, 'w') as f:
            json.dump(sample_lease_data, f)
        
        # Mock Observer to avoid blocking
        mock_observer = MagicMock()
        mocker.patch('json_leases_to_unbound.core.Observer', return_value=mock_observer)
        mocker.patch('time.sleep', side_effect=KeyboardInterrupt)
        
        core.active_leases = {}
        
        core.main(
            log_level='INFO',
            source=temp_lease_dir,
            domain='test.local',
            unbound_server=None,
            config_file=None
        )
        
        assert core.default_domain == 'test.local'
        mock_observer.start.assert_called_once()
        mock_observer.stop.assert_called_once()
