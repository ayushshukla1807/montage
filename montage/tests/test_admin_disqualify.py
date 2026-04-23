import pytest

def test_admin_manual_disqualify(api_client):
    # Testing the manual disqualification endpoint
    fetch = api_client.fetch
    
    # We assume a round is active and entries exist, similar to test_web_basic.py
    # Get campaign details
    resp = fetch('coordinator: see all campaigns',
                 '/admin',
                 as_user='LilyOfTheWest')
    
    if not resp['data']:
        return # Skip if no active campaigns in test DB
        
    campaign_id = resp['data'][0]['id']
    
    # Get campaign detailed view
    resp = fetch('coordinator: get campaign details',
                 '/admin/campaign/%s' % campaign_id,
                 as_user='LilyOfTheWest')
                 
    if not resp['data'].get('rounds'):
        return
        
    round_id = resp['data']['rounds'][0]['id']
    
    # Get entries
    resp = fetch('coordinator: get round entries',
                 '/admin/round/%s/entries' % round_id,
                 as_user='LilyOfTheWest')
                 
    if not resp['data']:
        return
        
    entry_id = resp['data'][0]['id']
    
    # Pause the round first (required to disqualify)
    fetch('coordinator: pause round',
          '/admin/round/%s/pause' % round_id,
          {'post': True},
          as_user='LilyOfTheWest')
          
    # Disqualify the entry with a reason
    resp = fetch('coordinator: manually disqualify entry',
                 '/admin/round/%s/%s/disqualify' % (round_id, entry_id),
                 {'reason': 'Failed GDPR compliance check'},
                 as_user='LilyOfTheWest')
                 
    assert resp['status'] == 'success'
    
    # Re-activate the round
    fetch('coordinator: reactivate round',
          '/admin/round/%s/activate' % round_id,
          {'post': True},
          as_user='LilyOfTheWest')
