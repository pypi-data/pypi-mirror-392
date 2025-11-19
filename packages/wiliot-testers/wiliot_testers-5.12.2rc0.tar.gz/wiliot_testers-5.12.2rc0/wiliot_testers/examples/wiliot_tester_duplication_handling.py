"""
  Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

from wiliot_api import ManufacturingClient
from wiliot_testers import WiliotTesterTagTest, FailureCodes


def is_duplicated_tag(all_passed_tags, adv_address, payload):
    # check if adva was already passed
    if adv_address not in all_passed_tags.keys():
        return False
    
    # check if same adva was received from different tags:
    try:
        # cloud connection
        client = ManufacturingClient(api_key=API_KEY, env='prod', owner_id=OWNER_ID)
        
        # resolve current test packet payload:
        payload_current = payload
        external_id_current = client.resolve_payload(payload=payload_current, owner_id=OWNER_ID).get('externalId')
        print(f'resolved for adva: {adv_address}, current external id: {external_id_current}')

        # resolve previous test packet payload with the same adva:
        payload_previous = all_passed_tags[adv_address]
        external_id_previous = client.resolve_payload(payload=payload_previous, owner_id=OWNER_ID).get('externalId')
        print(f'resolved for adva: {adv_address}, previous external id: {external_id_previous}')

        return external_id_current == external_id_previous if external_id_current is not None else True
    
    except Exception as e:
        print(f'could not resolve duplication payload for {adv_address} due to {e}')
        return True  # duplicated tag since no additional data is available

if __name__ == '__main__':

    API_KEY = ''
    OWNER_ID = ''

    # init wiliot tester
    wiliot_tag_test = WiliotTesterTagTest(selected_test='Ble_Test_Only')
    all_passed_tags = {}  # dictionary with the passed tags where the key is the advertising address and the value is the payload e.g. {adv_address: payload} {"06825CF7600C": "AFFD0500003935D6CE90B8457DFEBE3F5D82421D09EF9D6244CFE952E6"}

    # run test on one tag location
    test_result = wiliot_tag_test.run(need_to_manual_trigger=True)

    if test_result.get_total_test_status():  # similar to the function is_all_tests_passed()
        # test pass
        selected_tag = test_result.check_and_get_selected_tag_id()
        test_payload = test_result.get_payload()
        if is_duplicated_tag(all_passed_tags=all_passed_tags, 
                            adv_address=selected_tag, 
                            payload=test_payload):
            # duplicated tag:
            test_result.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
            test_result.set_packet_status(adv_address=selected_tag, status='duplication')
            print(f'DUPLICATED TAG {selected_tag}')
        else:
            # pass tag
            print(f'TAG {selected_tag} PASSED')
            all_passed_tags[selected_tag] = test_payload
    else:
        print('FAILED TAG')

    print('done duplication handling example')