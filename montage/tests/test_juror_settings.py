import pytest

def test_juror_update_settings(api_client):
    # Test setting consent to share votes
    fetch = api_client.fetch
    
    # 1. Check initial state or set the setting
    resp = fetch('juror: update settings',
                 '/juror/settings',
                 {'consent_to_share_votes': True},
                 as_user='Slaporte')
                 
    # Validate the data returned
    assert resp['status'] == 'success'
    assert resp['data']['consent_to_share_votes'] is True
    
    # 2. Revert setting to False
    resp = fetch('juror: update settings to false',
                 '/juror/settings',
                 {'consent_to_share_votes': False},
                 as_user='Slaporte')
                 
    assert resp['status'] == 'success'
    assert resp['data']['consent_to_share_votes'] is False
