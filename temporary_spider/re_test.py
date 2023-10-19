# -*- coding: UTF-8 -*-


from tools.proxy_get import queue_empty

# proxies = {
#     'http': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333',
#     'https': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333'
# }
#
# response = requests.get('http://ipinfo.ipidea.io', proxies=proxies)
# print(response.content.decode())

# curl -x proxy.ipidea.io:2333 -U "liulijun584268-zone-custom:9TL39WvUnboIdOI" ipinfo.ipidea.io
import requests

# ps = queue_empty()
# proxies = {
#     'http': f'http://{ps}',
#     'https': f'http://{ps}',
# }
proxies = {
    'http': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333',
    'https': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333'
}
headers = {
    'authority': 'cn.wsj.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'ab_uuid=980526fb-482b-4e01-a557-dbc16d406e27; usr_bkt=63L1D4y2F9; dnsDisplayed=undefined; signedLspa=undefined; _pubcid=5910c915-28b9-4102-aaaa-8fc6d7770fe0; _sp_su=false; permutive-id=eff631df-559b-4936-b318-f6aa350c8592; _pcid=%7B%22browserId%22%3A%22lm8xxkd192nprrrv%22%7D; cX_P=lm8xxkd192nprrrv; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIE4AmHgZl4CsArgA4BANgDs4gQEYOvACwgAvkA; _pubcid_cst=kSylLAssaw%3D%3D; wsjregion=asia%2Ccn; gdprApplies=true; ccpaApplies=false; vcdpaApplies=false; regulationApplies=gdpr%3Atrue%2Ccpra%3Afalse%2Cvcdpa%3Afalse; usr_prof_v2=eyJpYyI6M30%3D; utag_main=v_id:018b468d30f30017f9e7dbcebd510506f002506700bd0$_sn:1$_se:1$_ss:1$_st:1697697540149$ses_id:1697695740149%3Bexp-session$_pn:1%3Bexp-session$_prevpage:CWSJ_Home_World%3Bexp-1697699340161$vapi_domain:wsj.com; AMCVS_CB68E4BA55144CAA0A4C98A5%40AdobeOrg=1; AMCV_CB68E4BA55144CAA0A4C98A5%40AdobeOrg=1585540135%7CMCIDTS%7C19650%7CMCMID%7C08390166715493864591348617732617325288%7CMCAID%7CNONE%7CMCOPTOUT-1697702941s%7CNONE%7CvVersion%7C4.4.0%7CMCAAMLH-1698300541%7C6%7CMCAAMB-1698300541%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI; s_tp=3706; s_ppv=CWSJ_Home_World%2C26%2C26%2C963; s_cc=true; cX_G=cx%3A2jbqlwaqih0ck311gsoiz5rhbk%3A2tjnc9oym9st9; _ncg_domain_id_=016c6f84-b0c6-4306-8fc1-2b33402e9435.0.1697695749629.1760767749629; _scid=c48cd52d-b140-43bf-9ea2-73ce14f82b53; _scid_r=c48cd52d-b140-43bf-9ea2-73ce14f82b53; _gcl_au=1.1.687707285.1697695750; _uetsid=05606d706e4611eea45705cca1ccd451; _uetvid=0560b3006e4611eeb4c1554468a82989; _li_dcdm_c=.wsj.com; _lc2_fpi=7880a1137012--01hd38tqppavyysp0j2jp58d2z; _lc2_fpi_meta={%22w%22:1697695751894}; __li_idexc=1; __li_idexc_meta={%22w%22:1697695751897%2C%22e%22:1698300551897}; _cls_v=cb60c888-4fe5-416f-8c19-78244a95def4; _cls_s=a025d9f0-87d0-4b9d-823f-c173e8b15ad2:0; dicbo_fetch=true',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

response = requests.get('https://cn.wsj.com/zh-hans/news/world', headers=headers, proxies=proxies)
print(response.status_code)
