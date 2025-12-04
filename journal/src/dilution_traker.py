
from curl_cffi import requests, BrowserTypeLiteral, CurlHttpVersion

session = requests.Session()

inputs_url = 'https://843384880e12.8cf5c68d.us-east-1.token.awswaf.com/843384880e12/16724fb3a115/inputs'
params = {'client': 'browser'}
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
    'origin': 'https://dilutiontracker.com',
    'priority': 'u=1, i',
    'referer': 'https://dilutiontracker.com/',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
}

inputs_r = session.get(url=inputs_url, params=params, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate='chrome', verify=True, allow_redirects=True)
challenge = inputs_r.json()
response = {'challenge': {'input': 'eyJ2ZXJzaW9uIjoxLCJ1YmlkIjoiZDg3NTdhY2QtYWZkMy00NjBkLTg2ODMtNmRkZjU0OWQ5YmU4IiwiYXR0ZW1wdF9pZCI6IjQ2YWM5N2EwLTJkZGItNDk2Ny1hZjY0LTFjMzJmZDlhZTM1OCIsImNyZWF0ZV90aW1lIjoiMjAyNS0xMi0wOFQwOTo1MzozOC43NDg2MTU5MDJaIiwiZGlmZmljdWx0eSI6NCwiY2hhbGxlbmdlX3R5cGUiOiJIYXNoY2FzaFNjcnlwdCJ9',
  'hmac': '2AFOfI1ePLxOljIkURC3o36hVYjJlLbIovLueJh1sGA=',
  'region': 'us-east-1'},
 'challenge_type': 'h72f957df656e80ba55f5d8ce2e8c7ccb59687dba3bfb273d54b08a261b2f3002',
 'difficulty': 4}

verify_url = 'https://843384880e12.8cf5c68d.us-east-1.token.awswaf.com/843384880e12/16724fb3a115/verify'
params = {
    "challenge": challenge['challenge'],
    "solution":"4",
    "signals":[
        {
            "name":"Zoey",
            "value":{
                "Present":"C+m6GkVwuMJIlS+I::2b44d2236a6c66a458b882677660d4e9::29fbf66ea687ed822230c90eba22413e227acf3af80d4217b56a5538bb389ae674ed98b5ccaaf2c00b1381a06e0f5af867393d3aa21f1714c8412738d9a015f6d06d07c0989519d8a451011c4ddc04c56ccb42e4eca2b0fea69880112d056b0f4ef1844b0548056acfdb462f0210cda47d4452332f4632fb40decde58abe34fa0c55f402803e8d81dcaade448a477527903328258c3db60d6a9a7934db289c56c57ae4f6ff94d62f2acacbfe31494f0108d07660edd81402ec828c30493ff2666010323d28f18e95bc8019f7ae98215e60585542966b1ec8b65ce2e76066287dd78b8b9e4ed8416f335992104d1e25a272a5f80f6450affe484d745e2f14cce1ca5132fd9853192add4153e0f4727aa164fb487e9e1fdf27f9274352995c093f5fb1b8b79a51b8b84f240719167603b450cad13457c34dfbea3834c62bad734e992f8d9014e92a5c3538e1d7d9c04d564cd48ea76b033bc945af7fffeffa4bdcdf336c37780ac6d83e32fd1a1f297072d7fa67ea8b0e138c681c0ead531808ad9bcb1c854d3b0665ae81cbc327edc6d12717607ee2cf3c2433f10d558947a4795198008ace11cf104040935145487f6342cdb7d8f8c7bc6809d0be6ae7c9b79d58c0f1d8e0159b4452e3ab768e6ab4b81d546e1e76c847050055525d139cc8e9727f06911f86619eba550d32216532294d0f689ee3d04b38a71ea79ad87fbcec942f943c7215119996057eb5914683d21f59121e0b38f0fb3b75b468d6ed58c3e7dec3d02b8afb5650f65deabacfdedc0661792a0de845f9b5ef1d237970b69677eeba4d36a02e9e6f21831fc540b906eb9d2b69fda20649a74ac719fb3ff088ba2b39433fdc758e0d6d1c734196db8237bef98e87b7cfb41012617cd61c053ddc54503eec09a8f8ca9eaf15faffc04fd94eb4a8eb329fd701d7a00425731849091829750551c1055ce02f05a734d341733694f94519e53c4aac3e00612b8f966b65a2520275669319303643a545a2952cf721f950518418322a75272a44c210cb1cb54b109dfd26cdf825ee933c06f7adb950068f7514b2d7460fc0e592c565a1c0880d6aef52f34f02d0512f13ec5168a952f7249521311a37d4521d749db25075ced976880967912f02afc44bffab7ee05703d291a7d939a7182e238329fe5dd53862800e636be67789d9ff6c1a81044c5cedd090dfd1ff4e92ee976afade3f385e181453fc2d9967b1f1c9a908303861f6479ca94d790e2219ce0492e57b468dd18d6e8056b596af952aae5629472a096c1f5641dff700848ff0b8dd1d9d58f97ce4bc6847696afc7e5f7c52e12def162736f6ce98175960c3ddd20c360b77e80301547c7757bef0b5b7fff96b5620f8da0e65a4fb0aac50111acae7b606e7b73e050c55a569871329649d3c0ea97f0830afaa77f944f2cde28abd5111294f5755194d59ff16f4e56bcd2ef946c8b51b2fa3efee20443373fe00eb86e7267eaa3a7add7856a2f24a10dd3c6aa06d65f4621715b4d445038fbbb49c2e80d5bcf672ae2b8da2d39a3c75139993626f51b493d228604a87835bc542521b6282a56cc94ca00363d0456d05075d79a0b8905f0c39f5917af2da3af512e3794924ebd83d9df2c84412e28106a43770b876377f19aae3bb52d0e399c5b5c8b212dd38801cd7bf6b87f5cccea5ac42e698d0ebdc9e3b6165f68b8df4641de29dcebecf0af98a66c222d64de16a0f96871fb48bdd00b493f753db470ad91a05cd1127095f8d65fa471d8de360153cbdaa1e24e416786d84237b0230ecad04b35d41e579b38da3e425bb8b08fa8eb8123f894e63c36238530b0ef074c147f92420ed7c0c4f158e0672a1216fbe83eeab30654096a6b8e982118504607ce69247d431e0ea474f9399fc0691f34ae43535954875941c62df75e0d1a192023046211979f5366569c236c35b756a3749a167e37f3ccebfbe23e95f618f4ac8688f5313f0831c2db8580584563b207a66712d652eb844d6ec9ade5b766d4312918c9c91c823e69a98797859fb04e76c74b8ffbc18fe04943f9a55a2304b9a98c3d63d6ccd4b36fce6f8d589e9f1ca7d52c5aa48ae164b66add1badb10cfe4ce1324d8dca83fe9a0dad838ebbf1c12d4a5aa929c5311a5fb43a59d6ce310852f62e24badc9f095ed4cee7ce4b7e9dd138d35a3dfda9e88c50cc76ec15b436d66a8fa1da58b4a83c97e990a2f7b86b9f2e1b78c73beedeeb507ed595a4064c041f70393e8cae91be117aff218ba2574c82b4a47e6ca22d8aa30d8e017ca27e727c6bf4e782ea6a954014256046a9cb11cebbd8e1f3be43d319aa4688461a07c87e48d207bc02f608c49eade9fb69c01f5af2d92d4f48947596168068d6b82cd1f0b6a956614e8158a7de834c4d008397a0e7d39ff4ca6845e5b0a94d3b2f91c15b48b8aadaadbe36805316f4a6e0e712bb8c804909d14ae88657b5515c1a035ad1cd123ff1e29b5625fd523d361b278632866dfc198542cef8a16d5883627d3ff60cf11d175b02b27453c997580bcf0ce7b54b63b461376774559bfca69aa02785576b2db68ec00f3539d39ae6c9988112ceafa6f5271590ece84eeb0f440c976a4e8f580d5f093c45604ac94d94a7e6084ea2a1e06f3589bd86e1f9c68a87bfde232a5e04f80d9a5ac2115cd6621b8f780bead62cc4ce0712825389f731e3317f5645c9aa19325c47359be57031a41081b0becace0b9018553fc6a657f44ab8852a359349e1604db676c80cc2dc49f770d890ef6bea3cf0c301d875efb30c51200843e551312c028f86f5e185119bf99fbe93e8c64ff8e630d5fbf3198ef78d44558e43921a086f93c316cda25a28f38b5a1bd92b41556752a6f83992c898ebc0e69b393e6c4aee5db239b3e3120eb3cf24e37d792acd105995591c82ed7e5a32842ca8a378aecf352c67ef7547d6bc9802fe95c7b0d9a1987209489ff55864798e6974659280ded72a1239f1315f43a5191989aee4b5660214cc3cc93c740ff312c22e8909653be815fc76d4f6abb3ff8676f14d1f4a7a99b64eabcc4ca043ff05a03e9bc7b7a3eefbddb7e8de7261ba930f30c545e8d9e7f23c2173f71ae1997a39f557901e2b2ff526feffc01ae4dd18251581411bd44a5c63a9cc9be9c85137d3f4bc2828befc241d90830dcd89a418acf27868bd6a196b2f6c05f5ebbbfcd4e8dc53517acfdbf576d30cf0e872a9f79d7f708168f9ce4e2e384a8a716f6e1b2a8e7c5ad86d2ea00526751776bbfa407d70d20f4d1eb3d3ce6d8604f652ea4c28eabf50cb5ff9c9d960e3678eecea8787d42bcbf011bc5d6903c338b76bccfd2558c9ce0e264aaf9b2d8ec044df590f3bf141136e91abadcdc958cc0b19d2f2fa97c33adb791dfcd423d6c529ae563cd00a37bae725d91437a8402d1e165416dcd1feeca061f299e74e27d5d1297d207d9b5d0a00151aab4e6db483e487c8a2cc87c15a171b5abdcc35a5747a1e367036fc4c5762de2d4f467c75ee2f37e1fefea052ecfa0765b0c8575dadbf059b958ad7f232da5a89001578ba4ceaa02fee927007df941118618e7037f42ed8af01d84eaf82826fe5aa15178c933f472151571bb7b67a91fe9380b3ab5102b0ff17daacb33ff9e69f264d96b33dc6b9bc74e6cbf7d00ade5858cf2a7db93091d775eafc03a7d767cf5d5db4b58e062faebbea1bf3d2b24db3bf8e9b218b9a6a0b84f4a0d6a7e62f09b26503e719e131d5b4f3c98344af118f7423b3c4ed2b6b4512d2f52c4e66a9af94f4f4909c3c281dc8c4625101242435f3ec0e21d6355d3ba39ad27a6e623126489aa2bc9c83a3421cd1678b04abda9fc7f1fb22be050d8e79aedb9b7ceda7f5b6fb26024636f55432ef57878bc364be1bfd21602a31e548bae179ecc017c3578c5026da0567c864b6825423540bd9c6fd8a68391d29a2828b27e29f8015795354a7f67644ad4b085e9df495354978d13102b40b4081036d7bba3dd2223d52203d2ecfe632a3d72ea9236fcd754bf1640ea8a964d2599589b9d035e9e186fe1932e3365a84b3dd9b756f3540a6ae781977120084403371126bc6429f47a92771db2bb9de7e177c4615a883f309f402833ae6bda529de20c50b24082da106ca41f09a4ac93e989f3d481e3e31d95e93223267e0fc165a33e9bc9ea8cf5603615b13316d57ea308ddda88953bc89d2e74548f47369c52e8c376ffeeab62bd0ec084cf2c0085da457d85f2c0c70e8c59115976c14c2235259da5f5b104a62789de5bf34afa6c68e5fed18cc665d333f9f5f726c5b3547c6e757a5e26e62503c8a932a7cfa6c69d0db0cc3767338fe6b94f7bcc599e15e71063eaae1597677da5ae87069e0558209a68fd21a2eb25ba6c4887c65cc81797e613d86fb83336e6bc0deea7e8481aa5e82898b48f51b754eefc9a188698865441404141f02883978d81834d2ab45497efdc7a6ae81b5e015b9099a2e33d86a7f439f9ec010b73f74a982d89bac2682753e121937d8dec1df15f49f33e2503a5beec6ed2d121ba977d1c323d9b73fd3cc6e1a68543fbf1cc10ce032e10f5ef31ec752577f25151dc974360437ac84f9fb145b1fbbd523c7e93e421c41ed61baee6d50507a2f4ca5995ab2e02edd154453b982d405818d323de898259284e684d1074f9ea68188c064c11e752b872752dfb0f6591a920dece7dd23a40c09040aeb3afc6bc9da3d319819ecdfc43f79b41348f9efe105aeab97e4532e1b8a76f2887ed563196b727388ab4d5b987cad87fe140061ed546e34b822d2b64bbd4faeed3a1219cd6e50ca4fc90a959352a2a6646d063e557e9d9f99840f4cadbee18950777d2f7eebc1e1de2fcbc44d9223f258121d67ca00f98808a002bc93e1a75c631f3fa901fd7db8f4158db1ef16b1698a77c2e1bab48c769155eb47c1bd52f08cf346e49d444872c31ffc141d437620081e685fe5e656105897c6c4b7b59ad0b2586f1e363b1fa35232de452c97f9108ffbcd56980be41271c95693a429226d8b2ce67298ad8f36335e50ae4e0c184e936e75e5e64ea3688e72b0020a1f3079b171541a592fb1d8de90fc3bbe32b004f26e5dd0dfbe3d92d864dc03170798eac193028c54792163126339b68b34d467a999acb09870e46ec28da9df358d8fd14701495bf5e0de49653974776dfd0f97f4155092dc70bb5841509221fcc78b8fa5e2b3a5653f846c3d29d4f29415ac47bccaeb85fc498"
            }
        }
    ],
    "checksum":"517F44CF",
    "existing_token":"01f3e7d2-bea1-428e-b98d-24057ae9a29e:EQoAj81iPlwmAAAA:K4F4stA6OG94mQedwV21b0kIX7CJtvvgisX4ACG+kKC+/P0mxkQ+hVt+ShugfgBo+8nFLjGbui6oYvcN2xU1WbALeUA/CMr7L+Oxv+SZrQ5qq9uZMY79VVCP09Bk0r8IU5lCVuz+QAYZzmV39T7p2enr0DfWsDMzK72yspDKdKEfQksR6pEPWnrLz1eOyTAT38zd+DV6w8HaaHgkIf+rKqYF+Mx2QHiRWFgV28bC8AvnNs8Uv5NLDHU+mOsZLSE5z0kpAN1sCN/HOw==",
    "client":"Browser",
    "domain":"dilutiontracker.com",
    "metrics":[
        {"name":"2","value":1,"unit":"2"},
        {"name":"100","value":1,"unit":"2"},
        {"name":"101","value":0,"unit":"2"},
        {"name":"102","value":1,"unit":"2"},
        {"name":"103","value":16,"unit":"2"},
        {"name":"104","value":0,"unit":"2"},
        {"name":"105","value":1,"unit":"2"},
        {"name":"106","value":0,"unit":"2"},
        {"name":"107","value":0,"unit":"2"},
        {"name":"108","value":0,"unit":"2"},
        {"name":"undefined","value":1,"unit":"2"},
        {"name":"110","value":0,"unit":"2"},
        {"name":"111","value":19,"unit":"2"},
        {"name":"112","value":1,"unit":"2"},
        {"name":"undefined","value":1,"unit":"2"},
        {"name":"3","value":9.199999809265137,"unit":"2"},
        {"name":"7","value":1,"unit":"4"},
        {"name":"1","value":56.5,"unit":"2"},
        {"name":"4","value":22.90000009536743,"unit":"2"},
        {"name":"5","value":0.09999990463256836,"unit":"2"},
        {"name":"6","value":79.5,"unit":"2"},
        {"name":"0","value":152,"unit":"2"},
        {"name":"8","value":1,"unit":"4"}
    ]
}

verify_r = session.post(url=verify_url, json=params, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate='chrome', verify=True, allow_redirects=True)
token = verify_r.json()['token']
verify_respnose = {'token': '79a7ffa0-273a-4b6e-93a6-00e547656655:EQoAmohEQmZyAAAA:dRoAb5OidwcxC9o3yQ0eTsKXX4nK8kR99/kbZ+8k9CkkFG1Yy8BFXKG8fVDBb5CofA/YEbzRWwDKzbC5f/4DWoU1NMu8ESVPHkhBlqZM9YKlbdaZv0HVqXvfOhN91pPzj7swPBNdz46TQblrDPazZlrgjq9qzNgZQFpnmzKJZgT5HPLjWql05jgxCdvSy+ULcQCIaY33TfNpj40DJfVjOxg7rxrqZwTK8GS+J06X0ZROWBVzztZfPOb4b5Cb/jADDvnlG8IHWrgM1Q==',
 'inputs': None}

ping_url = 'https://api-iam.intercom.io/messenger/web/ping'
params = {
    'app_id': 'qkbpyl27',
    'v': '3',
    'g': 'a3219f4e5393dd90eb19f78c49c67cb34215bdb8',
    's': 'a4834216-556c-4679-9786-64bd10daa8c1',
    'r': 'https://dilutiontracker.com/register',
    'platform': 'web',
    'installation_type': 'js-snippet',
    'installation_version': 'undefined',
    'Idempotency-Key': 'bc8f0a00171bc3df',
    'internal': '{}',
    'is_intersection_booted': 'false',
    'page_title': 'TGL | Dilution Tracker',
    'user_active_company_id': 'undefined',
    'user_data': '{"email":"dcaronm@gmail.com","user_id":"0bf0d6a3-5a6d-4ee0-a46c-dd5b880ac731","anonymous_id":"f0c6a37e-6cef-40cc-9118-171410a12943"}',
    'source': 'apiBoot',
    'sampling': 'false',
    'referer': 'https://dilutiontracker.com/app/search/TGL?a=3f5b9d',
    'anonymous_session': 'dVo5Q21FLzVyY2JKMGR4UUROZHVIRUZhbkhRNHByNUk2QkNrdEdZRlNhVDhCajRPZGtMdDFnOXp0NVFOVm80VDZsU0d5Z1JlKzAvTzBTdHVSaG9oZ2RjQ2d3S1pRMjdOeDY0ZHAwRnl3Slk9LS1iamZmZE10dmdhK0M3bTYvWCswaW5BPT0%3D--c10fce0a4867d4bd6d5f207587d5f7d64c2df512',
    'device_identifier': '813198c9-7a51-4031-a94f-de02c2b183f9'
}
ping_r = session.post(url=ping_url, data=params, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate='chrome', verify=True, allow_redirects=True)
data = ping_r.json()
ping_response = {
    'app': {'name': 'Dilution Tracker',
  'audio_enabled': True,
  'show_powered_by': True,
  'team_intro': 'Ask us anything, or share your feedback.',
  'team_greeting': 'Hi there 👋',
  'messenger_background': 'background-1',
  'expected_response_delay_translation_key': 'a_few_hours',
  'launcher_expected_response_delay_translation_key': 'the_team_typically_replies_in_hours',
  'sms_notifications_enabled': False,
  'inbound_conversations_disabled': False,
  'office_hours_response': 'Later today',
  'help_center_site_url': 'https://knowledge.dilutiontracker.com',
  'messenger_logo_url': 'https://downloads.intercomcdn.com/i/o/288560/7abd2f526688b38151819031/653104a47558fe297a574f1f30f72626.png',
  'user_conversation_gifs_enabled': True,
  'user_conversation_voice_notes_enabled': True,
  'developer_workspace': False,
  'upfront_email_collection_setting': 'always',
  'temporary_expectations_message': None,
  'localized_expected_response_delay_short_text': 'Back later today',
  'localized_expected_response_delay_long_text': "We'll be back online later today",
  'help_center_id': None,
  'article_auto_reaction_enabled': False,
  'use_cache_for': []},
 'user': {'id': '68d24693d02a5d8a8c8e2df5',
  'role': 'user_role',
  'locale': 'en',
  'has_conversations': True,
  'country_code': 'es',
  'last_contacted_at': '2025-12-05T14:25:21.279+00:00',
  'new_session': False,
  'help_center_require_search': False,
  'requires_cookie_consent': False,
  'prevent_multiple_inbound_conversation': False,
  'user_assignments': {}},
 'client_matches': [{'user_id': '68d24693d02a5d8a8c8e2df5',
   'company_id': '-1',
   'predicates': [{'attribute': 'client_attributes.time_on_page',
     'type': 'duration_integer',
     'comparison': 'eq',
     'value': '5'},
    {'attribute': 'client_attributes.last_visited_url',
     'type': 'string',
     'comparison': 'contains',
     'value': 'dilutiontracker.com/pricing'}],
   'ruleset_id': 21176380,
   'ruleset_match_behavior': 'single_match',
   'ruleset_link_id': 21259400,
   'ruleset_link_object_type': 'chat',
   'serialized_object': None,
   'checkpoint_id': None,
   'notification_record_id': None,
   'matching_locations': [0, 25, 12],
   'extra_context': {},
   'contains_lca_predicate': False}],
 'launcher_settings': {'alignment': 'right',
  'color': '#0071b2',
  'color_dark': '#1a8bcc',
  'has_required_features': True,
  'horizontal_padding': 20,
  'instant_boot_enabled': True,
  'launcher_logo_url': None,
  'launcher_logo_dark_url': None,
  'secondary_color': '#2392ec',
  'secondary_color_dark': '#2392ec',
  'show_launcher': True,
  'theme_mode': 'light',
  'updated_at': 1765167035,
  'vertical_padding': 20},
 'modules': {'messages': {'google_analytics_tracking_id': None},
  'rtm': {'endpoints': ['https://nexus-websocket-a.intercom.io/pubsub/5-JFX3S25uWsi2CCsijwzjgd2vB_-sKxD00-esfeWwxjRr9sqp-2UuMHpLmhwEfGoediMC2gOuFHbbSAfI4uCCBnsQalnN1ZqGopTC'],
   'options': {'PING_TIMEOUT': 45000, 'PONG_TIMEOUT': 10000}},
  'metrics': {'enabled': False},
  'error_reporting': {'disabled': False},
  'customization': {'brand_name': 'Dilution Tracker',
   'messenger_logo_url': 'https://downloads.intercomcdn.com/i/o/288560/7abd2f526688b38151819031/653104a47558fe297a574f1f30f72626.png',
   'messenger_wallpaper': 'background-1',
   'action': {'background_color': '#0071b2',
    'foreground_color': '#ffffff',
    'foreground_color_low_contrast': '#ffffff',
    'background_color_dark': '#1a8bcc',
    'foreground_color_dark': '#14161a',
    'foreground_color_low_contrast_dark': '#14161a'},
   'action_contrast_white': None,
   'action_contrast_dark': None,
   'header': {'background_color': '#ffffff',
    'foreground_color': '#222222',
    'background_color_dark': '#14161a',
    'foreground_color_dark': '#f7f7f7'},
   'theme_mode': 'light',
   'launcher_logo_dark_url': None,
   'messenger_logo_dark_url': None,
   'custom_font': None},
  'home': {'header': {'background': {'enabled': False,
     'animated': False,
     'type': 'solid',
     'type_dark': 'solid',
     'color': '#2392ec',
     'color_dark': '#2392ec',
     'fade_to_white': True,
     'fade_to_dark': False,
     'gradient': None,
     'gradient_dark': None,
     'image_url': None,
     'image_dark_url': None},
    'content': {'greeting': {'content': 'Hi there 👋',
      'text_color': '#ffffff',
      'text_color_dark': '#14161a',
      'opacity': 1.0},
     'introduction': {'content': 'How can we help?',
      'text_color': '#ffffff',
      'text_color_dark': '#14161a',
      'opacity': 1.0},
     'close_button': {'foreground_color': '#ffffff',
      'background_color': '#000000',
      'background_opacity': 0.5},
     'show_avatars': True,
     'text_color_type': 'light',
     'text_color_type_dark': 'dark',
     'logo_url': 'https://downloads.intercomcdn.com/i/o/288560/7abd2f526688b38151819031/653104a47558fe297a574f1f30f72626.png',
     'logo_dark_url': None},
    'header_expanded': True,
    'identity': 'ai_agent'},
   'open_config': None},
  'features': {'checklists': True,
   'checklists_reminders': True,
   'inbound_messages': True,
   'inbound_lead_messaging': True,
   'inbound_lead_messaging_docs_site': True,
   'launcher_discovery_mode': True,
   'marketo_enrichment_installed': False,
   'hubspot_installed': False,
   'google_analytics': False,
   'single_page_app_rate_limiting': False,
   'cross_site_cookies': False,
   'cookie_secure_flag': False,
   'ticket_creation': False,
   'google_analytics_4_integration': True,
   'view_in_help_center_button': True,
   'customer_privacy_policy': False,
   'eprivacy_cookie_compliance_required': False,
   'persist_client_id_for_conversation_parts': True,
   'composer_is_not_hiding': True,
   'conversations_are_expandable': True,
   'unified_reply_expectations': True,
   'disable_fin_image_reading': False,
   'delay_tour_render': False,
   'disable_tickets_after_conversation_end': False,
   'new_mobile_notifications_enabled': False,
   'nexus_ably': True,
   'fin_latency_messenger_header_revamp_enabled': False,
   'disable_ticket_email_notification': False,
   'team_messenger_fin_messenger': False,
   'mercury_ui_changes': False,
   'enable_custom_emojis': False,
   'user_images_grid': False,
   'user_images_aspect_ratio': False,
   'fin_images_grid': False,
   'new_privacy_policy_layout': False,
   'fin_launcher_discovery_mode': False,
   'ai_titles': False,
   'always_get_salesforce_token': False}},
 'unread_conversation_ids': [],
 'unread_dismissed_conversation_ids': [215470958760393],
 'anonymous_session': 'WWtTN0tjZGRFN0YvVHdjWFVzTkI0MGt1N0tueXNqWmpFMS9qUVk5aDZtdTcwSzdVaEhUeGp5V2hKZ2hiOEs2dVVxcEVtVFhaUk41L3d0WVlYZmx5N1RUdzQ1Tlo2aWl4aFB6NzVydkZYZ0U9LS1xRHhOY3U4MThGblJoMUFsR2VoOGtnPT0=--5607c5ca7924f112dd765fa1f1f214261800fc30',
 'identity_verification_ready': False,
 'origin_cookie_domain': 'dilutiontracker.com',
 'cdas_breaching_limit': [],
 'checklists': [],
 'open_config': {'form': 'default',
  'open_to': 'home',
  'spaces': [{'type': 'home',
    'label': 'Home',
    'navigation_label': 'Home',
    'badge': None},
   {'type': 'messages',
    'label': 'Messages',
    'navigation_label': 'Messages',
    'badge': {'badge_type': 'unread', 'label': '1'}},
   {'type': 'tickets',
    'label': 'Tickets',
    'navigation_label': 'Tickets',
    'badge': None},
   {'type': 'help',
    'label': 'Help',
    'navigation_label': 'Help',
    'badge': None},
   {'type': 'tasks',
    'label': 'Tasks',
    'navigation_label': 'Tasks',
    'badge': None}],
  'user_has_tickets': False,
  'user_has_received_checklists': False,
  'user_has_live_newsfeed': False,
  'unified_style': True},
 'unread_tickets_count': 0,
 'session_expiry': 1765792112,
 'jwt_expired': False}

session_storage = None
telemetry_url = 'https://843384880e12.8cf5c68d.us-east-1.token.awswaf.com/843384880e12/16724fb3a115/telemetry'
params = {
    "existing_token":token,
    "awswaf_session_storage":session_storage or "null",
    "client":"Browser",
    "signals":[
        {
            "name":"Zoey",
            "value":{
                "Present":"nZab94XY3zuljJm7::9962e41afecfcb3546da4ee494741747::db10941a98eb717e049a3e61cdc28600d9c417653c0a89adb41152a4f8609e77cf01f529c92c3872c5ac2fc584abd4aaf3b276ff25aa95414049f9d19b1ec5020fb0e3b7993e82f1f23b258e8f5ac216c61b49bbac6fb326802af6977230bf3b5cc1be1736b924f24f8d92e123563d0eaa5a986ece75402cd85c2edb85df3f230818ddf577daf58c34188f81c536b68f2c251d987f1f788a6ddcd440c123ab5d46aa1903728e58d26958d164184c6189ab365c7449af7fc9cd9dde5c699b8aab63fc47352930f56dac16874560bb39a8cd132fb90f5b541ffbeb21e45070b18eae890031bf657399c627c328777335f66d2598379164dfe79cce663051a4794d7a125ae0840504e404eb65b83b9278a59caa40526b486bf8194afdd8f631ca4160ca804b345fb6d9d0fa22b7bbf21769f3788780bf7fc716b26f12a9344c4c50f65aa2d7777068581f6d9bc7298bccc9b89939e08ef0655dd7017b2be3c36ed92d227060b66854ba6a95d8683c28a77293a26b926ae193db27caf21cc5ec212df31f13fee63e614fa4481ed2e9be2831c5e8cc6347f446a47f3cab599148033a0b2a2b859eb27958a4c6ffff6bad39a87ea20d1741db869d3d92aa6ead956a8819db14a27e8e0a6c70d9563c3ada076c1912e2a9f82310913a91f1e19d87c0a23aa21c582ce2d6e5438a74d95220405f91ee28f210eb46"
            }
        }
    ],
    "checksum":"77E4AD24",
    "metrics":[
        {"name":"12","value":0.40000009536743164,"unit":"2"},
        {"name":"200","value":0,"unit":"2"},
        {"name":"201","value":2,"unit":"2"},
        {"name":"13","value":1.5999999046325684,"unit":"2"},
        {"name":"10","value":0,"unit":"4"},
        {"name":"9","value":2,"unit":"4"},
        {"name":"11","value":9.700000047683716,"unit":"2"}
    ]
}

telemetry_r = session.post(url=telemetry_url, json=params, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate='chrome', verify=True, allow_redirects=True)
session_storage = telemetry_r.json()['awswaf_session_storage']
"01f3e7d2-bea1-428e-b98d-24057ae9a29e:EQoApRxiOIVEAAAA:F0H694MRYxOGSiaRfn9nQ/kmO8dvoF/mWftv4N2UUGNn+Trq1++aX+kobnVady6p5GBxtduEd6c6xzv+Vic663+qSbODx4AvtiBLqKPDLdzZVamsUxmZ8hTto1BaaGOQ5MuhHD4YeE4VRTXQ45l2U5U79z8p/DOos7ggE70BE9vM2Ibew8e1V4TtGfx2kQk0QAF8JOQv9kxh1O4aTLs4cBakObrSLXhVA3mzuNZw5sdVeXk8n3/dZZFvhL+82xoMZ10F3y0iv/KiYUm+C4ySs+T5MVL5JYzS0PNBwm5IdDNqccBxrI4aeUiQGncKs0aB7Xlq6iGFDsfYYMeCp4HNT79KJJGdH5kuK/lgBVuE4U3/gi8UpbaG26BzcdYDhsSKg4r9BJlfj+aUjqz2afSyYD6B6Nzs7omZKJrgAbBn0Q=="
telemetry_response = {'token': '79a7ffa0-273a-4b6e-93a6-00e547656655:EQoArHtD9sGIAAAA:klWRqLLnwL+FXfGqhbUcM1iUl4UurgOcU2+kkfEKNvXuhXQJWPjEwiXL8pCHapUuKcUGA3Gv5b59MmoQ9uplLyHqCpd/j3BCaJ1fmHr14WhJIaYNJQOp6y+eSb2Ei1o8s1YnZn46vTJiYvZYZFV0WMf4/8CeUewq5MhXje/6NowO1JmACbMt8rwyfeYgH5pL/yKL9tnryGrmLw0UHLNjV8cK0D/CVQfJhxxccPmtgL3ojPzW0Rn+5lbGJ2RzXamXPyxQFSYzJKaiVw==',
 'next_interval': 100,
 'awswaf_session_storage': '79a7ffa0-273a-4b6e-93a6-00e547656655:EQoArHtD9sKIAAAA:Ocf+biuNxn3I/Db8KAKZ4ghAGFpw8jP7ctL98R9wBc3ouEv3QDMHN9gsveJomsiSYjXN1DEEsVwyo08EzIiw0grdX/H0ELs0zuOukxi4h14WWgaHbRqLE80+ZVdUGE5YZkkoOQMeW2rmwhj91qhpDmNMcRf9PwEUPQG1MEIhYCotJ3ne7KoSnyND1kcE5i0exKYJA1TIhocngJdQsLXIE4SjM80a0F+OnhIqO/fnthRJPoXXf4SF8lKMksxgwEouPeSy+fcYTpABykQd/n1WIjdDIh0DUwThas7VcIKzn4/npSWXYuu+hBDdIU+nVMi7wZIo/tAX/ScXhZ4GDPiMgjIJBXTe/8cIABGnm2nXgYCdodo1GOOu3Y5vMtzWIbJBBo5OCOH7s2CVw4jZOLDB38iKOxF3H3EZys+/9dWCtw=='}


symbol = 'TGL'
company_profile_url = f'https://api.dilutiontracker.com/v1/getCompanyProfile'
params = {
    'ticker': symbol
}
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
    'cookie': f'__stripe_mid=d8784eca-17de-4f35-bc29-a886b4815aee61ae12; \
                intercom-id-qkbpyl27=f0c6a37e-6cef-40cc-9118-171410a12943; \
                intercom-device-id-qkbpyl27=813198c9-7a51-4031-a94f-de02c2b183f9; \
                connect.sid=s%3AfbwzSHDFAgQYsCuajNNj0-gZjR5ulKiw.%2BMnh%2B6dbaDrBJNvUxxPDiDDQudipMPq2gThLZeSWWoU; \
                intercom-session-qkbpyl27={ping_response["anonymous_session"]}; \
                __stripe_sid=b4851d83-acdc-4ba4-b9ca-f9f84d334da9a2c0d7; \
                aws-waf-token={token}',
    'if-none-match': 'W/"273-prRMJ9HMttdyM1xPS8bfAZuZaVk"',
    'origin': 'https://dilutiontracker.com',
    'priority': 'u=1, i',
    'referer': 'https://dilutiontracker.com/',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'url': f'https://dilutiontracker.com/app/search/{symbol}',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-aws-waf-token': token,
    'x-referer':''
}


r = session.get(url=company_profile_url, params=params, headers=headers, http_version=CurlHttpVersion.V1_1, timeout=300, impersonate='chrome', verify=True, allow_redirects=True)


intercom-id-qkbpyl27 = "f0c6a37e-6cef-40cc-9118-171410a12943" 
intercom-device-id-qkbpyl27 = "813198c9-7a51-4031-a94f-de02c2b183f9" 
connect.sid = "s%3AFKDcG-xBMxzAVt-8cCavXg9Ujrq2H6j5.GU6y6rA1vg%2BhAz1AoNyrqdqKQMsE1VPPSK1NNfgRYd8"
intercom-session-qkbpy127 = "NStwRSswOEJCMlQzRGFLY2lIMVZlK2dUeU5PNnNiVG5BOHllR21FemFMRUtibEgxZlgyYnA4blg1Y0tBRHNJNXJ5b0lBMEJsdmVSc0YwdTcwM24vRThIQUd2Q0JFMDZyREcvYXBETXNBQ0E9LS1GZEVKUk9JdlpmdlJlRUFUUkQ1RGFBPT0=--0db55b69cb1baf887e6eb2cf5bb7914b21a2645a"
aws-waf-token = "79a7ffa0-273a-4b6e-93a6-00e547656655:EQoAevdDpzkoAAAA:2Z0xmC2QvF8zBOLTxWqnZ64r340R3eKyFF6ors3fGxvPtXAWQcEhBsEjYJDoahpUnYGY0JETVIb2S/+DAL9ZMSKhVdgG/r9D5pAJtohsYmnvKTqmmKVc8fR7ti16VJfuaB4cU0uoTZUPXgMji2EmMcoINSeSdReSMeqpTEak6oERzjQxLttgVp8dpjj+9HtXvQz/JaSLCeFEYCfcQxg2vHLYCzO+9DBb6Ci6+2Lv7gdh9+D/vJ6C23xo8iVt40jn0H+UTqNpNiglbQ=="
if-none-match = 'W/"4b7-/CeWLb39NIhgmQI0FI+sZwKP0bw"'
x-aws-waf-token = "79a7ffa0-273a-4b6e-93a6-00e547656655:EQoAnFtDHxJUAAAA:+9CL6cbO8RVvosoBJJvNMlG1zR2+H/WOOOUFDPj6j7uwvGd+J6cCTTPloe+VQuWagmZrn50tnJIhHt/GNxkRTvheLNoGso4+/mE75e16EaVyNV2H7EIPljU8fgzt3KYvhkFJX2bmp7vfrPb5pcRVVyHHc1KlhAfMfE20XLqUmWS4SMljJIeWszCELHuXBVFn4I52yJCC7s9j+0raQZe1V4sp0iQp9sqRO4gF28bkoIZoMV7d/EYA1bIymA6B33O7obTdhFH19+7QQQ=="