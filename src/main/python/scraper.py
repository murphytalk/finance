# -*- coding: utf-8 -*-
"""
Scrap portfolio performance page from brokers' website.
"""
from __future__ import division
import cookielib
import urllib
import urllib2
import re
import codecs
import logging
from time import sleep
import csv
from datetime import datetime,date,timedelta
from bs4 import BeautifulSoup as bs
from utils import ScrapError
from config import DEBUG

AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0'

def read_as(res, encoding='sjis'):
    return res.read().decode(encoding)


def parse_form_parameters(soup, encoding='sjis'):
    return dict((n['name'].encode(encoding), n['value'].encode(encoding)) for n in soup.find_all('input') if
                n.has_attr('value') and n.has_attr('name'))


def strip_str(s):
    return re.sub('\s+', ' ', s.strip())


def strip_str_from_first_matched_class(soup, class_name):
    n = soup.findAll(attrs={"class": class_name})
    return strip_str(n[0].get_text())


def get_digits(s):
    return ''.join(c for c in s if c.isdigit() or c == '-' or c == '+' or c == '.')

    
def write_html(fname, data, seq, encoding='shift_jis'):
    if DEBUG:
        f = codecs.open('{}-{}.htm'.format(fname,seq), 'w', encoding)
        f.write(data)
        f.close()
    return seq + 1

def read_html(fname, encoding='shift_jis'):
    f = codecs.open(fname, 'r', encoding)
    p = f.read()
    f.close()
    return p


class Broker:
    def __init__(self, proxy_handler=None):
        self.parser = 'lxml'
        self.proxy_handler = proxy_handler

    @classmethod
    def get_name(cls):
        return cls.__name__

    def build_url_opener(self):
        debug_level = 1 if DEBUG else 0
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=debug_level ),
            urllib2.HTTPSHandler(debuglevel=debug_level),
            urllib2.HTTPCookieProcessor(cookies))
        opener.addheaders = [('User-agent', AGENT)]
        if not self.proxy_handler is None:
            opener.add_handler(self.proxy_handler)
        return opener

    def open(self):
        pass


class Suruga(Broker):
    def parse_performance_table(self, raw_table, adapter):
        def strip_numbers(line):
            return [strip_str(x) for x in line.split('\n') if len(strip_str(x)) > 0]

        soup = bs(raw_table, self.parser)

        ##2014/1 Format
        #the ファンド別運用損益 table
        tables = soup.findAll('table', attrs={"class": "typeE2"})
        rows = tables[0].find_all('tr')
        '''
        from row #3 to the second last row are instruments list (the last row is summary)
        2 rows for each instrument
        '''
        for r in rows[2:-1]:
            cols = r.find_all('td')
            if len(cols) == 3:
                c1 = cols
            else:
                c2 = cols

                name = strip_str(c1[1].get_text())

                #strip new lines to get 残高口数 and  評価金額
                l = strip_numbers(c2[1].get_text())
                amount = int(get_digits(l[0]))

                l = strip_numbers(c2[2].get_text())
                market_value = float(get_digits(l[0]))

                #strip new lines to get 投資金額,discard 受取金額
                l = strip_numbers(c2[3].get_text())
                capital = float(get_digits(l[0]))

                #strip new lines to get 運用損益
                l = strip_numbers(c2[5].get_text())
                profit = float(get_digits(l[0]))

                #compute 基準価額
                base_value = round((market_value / amount) * 10000, 0)

                adapter.onData(name, capital, amount, market_value, profit, base_value)

    def open(self, adapter):
        site = 'https://ib.surugabank.co.jp'
        url = site + '/im/IBGate'
        target = u'運用損益'
        change_password = u'パスワード変更'

        opener = self.build_url_opener()

        #BS will assume utf-8 if the input str is not unicode so convert it to unicode first
        data = parse_form_parameters(bs(read_as(opener.open(url)), self.parser).form)

        data['USR_NAME'], data['MASK_LOGIN_PWD'] = adapter.get_login()


        #the server returns an automatic post page,parse the parameters out
        data = parse_form_parameters(bs(read_as(opener.open(url, urllib.urlencode(data))), self.parser).form)
        ed = urllib.urlencode(data)
        #the extra _PageID must be added
        ed = '_PageID=NoPageID&' + ed
        page = read_as(opener.open(url, ed))
        login_seq = write_html(Suruga.get_name(), page, 0)

        """
        Suruga shows an annoying screen if password has not been changed for 3 months
        handle this additional screen
        """
        if page.find(change_password) > 0:
            data = parse_form_parameters(bs(page, self.parser).form)
            ed = urllib.urlencode(data)
            page = read_as(opener.open(url, ed))
            login_seq = write_html(Suruga.get_name(), page, login_seq)

            #the server returns an automatic post page,parse the parameters out
            data = parse_form_parameters(bs(page, self.parser).form)
            ed = urllib.urlencode(data)
            ed = '_PageID=NoPageID&' + ed
            page = read_as(opener.open(url, ed))
            login_seq = write_html(Suruga.get_name(), page, login_seq)

        soup = bs(page, self.parser)
        l = [x for x in soup.find_all('a') if x.get_text() == target]
        if len(l) == 0:
            raise ScrapError("{}:cannot find target link!!!".format(self.get_name()))
        else:
            url = site + l[0].get('href').encode('sjis')
            page = read_as(opener.open(url))
            write_html(Suruga.get_name(), page, login_seq)
            self.parse_performance_table(page, adapter)


class UFJ(Broker):
    site = 'https://entry11.bk.mufg.jp/ibg/dfw/APLIN/loginib/login'

    def __init__(self, proxy_handler=None):
        #super(UFJ, self).__init__(proxy_handler)
        Broker.__init__(self, proxy_handler)
        #the default parser lxml does not work well with UFJ's pages
        self.parser = 'html.parser'


    def parse_performance_table(self, soup_table, adapter):
        def parse_value(s,name,ender):
            pattern = re.compile(r'%s" *type="hidden" *value="(.*?)".*'%(name)) 
            sub_s = s[s.find(name):]
            m = pattern.match(sub_s)
            if DEBUG:
                print "%s str:%s"%(name,sub_s)
                print "%s=%s,digit only=%s"%(name,m.group(1),get_digits(m.group(1)))
            return get_digits(m.group(1))


        #tag = u'＜特定＞'
        rows = soup_table.find_all('tr')
        #2014/1 Format
        for r in rows:
            #Fund name is in the first "txt" class
            fund_name = strip_str_from_first_matched_class(r, "txt")

            #the market value and profit are in the 2nd col
            col = r.find_all('td')[1]

            ##時価評価額
            market_value = float(get_digits(strip_str_from_first_matched_class(col, "market_value")))
            if market_value == 0:
                #this happens when this particular fund is just sold but still have buying schedule
                adapter.onData(fund_name, 0.0, 0, 0.0, 0.0, 0.0)
                continue

            ##評価損益
            diff = float(get_digits(strip_str_from_first_matched_class(col, "diff")))

            """
            Parse numbers. As of 2014/1, they look like below in the HTML

                 <dl class="sub flat_unit">
                    <dt>基準価額(前日比)</dt>
                    <dd class="base_value">11,257円 (<span class="number_plus">+27</span>円)</dd>
                  </dl>
                  <input type="hidden" class="base_date_ymd" value="2014年1月7日">
                  <input type="hidden" class="unit_price" value="11,718円">
                  <input type="hidden" class="capital" value="11,636円">
                  <input type="hidden" class="amount" value="42,671口">
                  <input type="hidden" class="way_recieve" value="再投資">
                  <input type="hidden" class="classification" value="特定預り">
            """

            ##基準価額
            #step 1 : get string like  11257+27
            base_value = get_digits(strip_str_from_first_matched_class(r, "base_value"))
            if DEBUG:
                print("base value:%s"%base_value)
            #step 2 : remove from + or -
            base_value = float(re.split('\+|-', base_value)[0])

            ##cannot get the following <input> elements by using class,possible reason : it should be <input/>
            ##So have to convert it to string and use regex to parse
            s = r.findAll("input", attrs={"class": "unit_price"}).__str__()
        
            amount = int(parse_value(s,"amount",u'口'))

            ##個別元本 => price per 10,000 units
            capital = parse_value(s,"capital",u'円')
            capital = round(float(capital) * amount/10000, 0)

            adapter.onData(fund_name, capital, amount, market_value, diff, base_value)

    def onetime_password_logon(self, onetime_password_page, onetime_password, urlopener):
        soup = bs(onetime_password_page, self.parser)
        data = parse_form_parameters(soup)
        data['PASSWORD'] = onetime_password
        data['_TRANID'] = 'AA012_001'
        logging.info("onetime_password_logon:%s" % urllib.urlencode(data))
        page = read_as(urlopener.open(self.site, urllib.urlencode(data)))
        return page

    """
    check_active is True when it is called from the UFJ active URL /active/UFJ/
    """

    def open(self, adapter, check_active=False):
        url = self.site + '?_TRANID=AA000_001'
        opener = self.build_url_opener()
        #parase the hidden parameters from form
        data = parse_form_parameters(bs(read_as(opener.open(url)), self.parser))
        #hard coded in js
        data['_TRANID'] = 'AA011_001'
        data['KEIYAKU_NO'], data['PASSWORD'] = adapter.get_login()

        #read the main page after login
        page = read_as(opener.open(self.site, urllib.urlencode(data)))
        login_seq = write_html(UFJ.get_name(), page, 0)

        """
        UFJ refuses the login if the login comes from a new IP address.
        It will show a "one password" screen, and request to input one-password sent to the registered mail address.

        So we will show a form where the one-time password can be input if this is detected.
        """
        expected = u'さまの代表口座'
        #detect if it is the expected screen
        if not page.find(expected) > 0:
            err = "Saw UFJ one-pass screen!"
            if check_active:
                #this is not called from cron, return the page
                logging.info(err)
                return page, opener
            else:
                logging.error(err)
                return
        elif check_active:
            #this is not called from cron
            return page, None


        #read the fund page
        url = 'https://direct11.bk.mufg.jp/ib/dfw/APL/ibp/toushishintaku/ToushinKouzaShutoku.do'
        page = read_as(opener.open(url))
        write_html(UFJ.get_name(), page, login_seq)
        soup = bs(page, self.parser)
        #find all tables
        tables = soup.findAll("table")

        #2014/1 Format
        self.parse_performance_table(tables[0], adapter)

class Nomura(Broker):
    branch = '08'

    def __init__(self, proxy_handler=None):
        Broker.__init__(self, proxy_handler)
        #the default parser lxml does not work well
        self.parser = 'html.parser'

    def parse_performance_table(self, raw_table, adapter):
        #2014/1 Format
        soup = bs(raw_table, self.parser)

        #the ファンド別運用損益 table
        tables = soup.findAll('table', attrs={"class": "tbl_dataOutputloop_02"})
        rows = tables[0].find_all('tr')

        ignore = u'野村ＭＲＦ'

        '''
        from row #3 to the  last row are instruments list, 2 rows for each instrument
        '''
        for r in rows[2:]:
            cols = r.find_all('td')
            if len(cols) == 8:
                c1 = cols
            else:
                c2 = cols

                name = strip_str(c1[1].get_text())

                if name == ignore:
                    continue

                #数量
                amount = int(get_digits(strip_str(c1[4].get_text())))

                """
                vary dirty HTML, has to parse number out of string like
                  --<br/>7,738</td>
                """
                if c1[0].get_text() == u'外投':
                    #基準価額
                    s = c2[2].__str__()
                else:
                    #基準価額
                    s = c2[1].__str__()

                price = float(get_digits(s[s.find('<br/>'):]))


                """
                Parse capital and market value from :
                  <td class="dottedline3" nowrap="nowrap"> 55,367<br/>53,529</td>
                """
                s = strip_str(c1[6].__str__())
                s = s[s.find("nowrap"):]
                l = s.split('<br/>')
                ##元本
                capital = float(get_digits(l[0]))
                ##時価評価額
                market_value = float(get_digits(l[1]))
                ##評価損益
                profit = market_value - capital

                adapter.onData(name, capital, amount, market_value, profit, price)


    def open(self, adapter):
        target = u'お預り資産'

        site = 'https://hometrade.nomura.co.jp'
        url = site + '/web/mfCmnCauSysLgiAction.do'
        opener = self.build_url_opener()

        #parse the parameters from the login page
        data = parse_form_parameters(bs(read_as(opener.open(url)), self.parser).form)
        data['btnCd'] = self.branch
        data['kuzNo'], data['gnziLoginPswd'] = adapter.get_login()
        data['loginTuskLoginId'] = "N{}{}".format(self.branch, data['kuzNo'])

        page = read_as(opener.open(url, urllib.urlencode(data)))
        login_seq = write_html(Nomura.get_name(), page, 0)

        soup = bs(page, self.parser)
        l = [x for x in soup.find_all('a') if x.get_text() == target]
        if len(l) == 0:
            raise ScrapError("{}:cannot find target link!!!".format(self.get_name()))
        else:
            url = site + l[0].get('href').encode('sjis')
            page = read_as(opener.open(url))
            write_html(Nomura.get_name(), page, login_seq)
            self.parse_performance_table(page, adapter)

class Nomura401K(Broker):
    #web page renewed on 2014/1/10
    def open(self, adapter):
        site = 'https://401k.nomura.co.jp'
        url = site + '/dc/auth/main'
        opener = self.build_url_opener()

        account, passwd = adapter.get_login()

        page = read_as(opener.open(url))
        login_seq = write_html(Nomura401K.get_name(), page, 0)
        #seqNo, WBSessionID, action = parse_hidden_parameters()

        LOGIN_PARAM = 'actionBase=login&actionReqest=_Authorize&_PageID=Login&_ActionID=loginB&browser_kind=5.0+%28Windows%29&browser=N&site_id=login&_ControlID=LoginControl&siteuser={}&sitetype={}'
        #url = site + action
        page = read_as(opener.open(url, LOGIN_PARAM.format(account, passwd)))
        login_seq = write_html(Nomura401K.get_name(), page, login_seq)

        LOGIN_PARAM = 'actionBase=login&actionReqest=_waitBalanceData&_PageID=LoadData&_ActionID=loaddataB&_ControlID=LoginControl'
        #url = site + action

        while True:
            sleep(3)
            #seqNo, WBSessionID, action = parse_hidden_parameters()
            page = read_as(opener.open(url, LOGIN_PARAM))
            login_seq = write_html(Nomura401K.get_name(), page, login_seq)

            soup = bs(page, self.parser)
            bd = soup.findAll('body')[0]

            if bd.attrs['onload'].find('submit()') >= 0:
                break
            elif login_seq > 30:
                raise ScrapError("Nomura401K login seq exceeded limits:{}!!!".format(login_seq))

        data = parse_form_parameters(soup.form)
        url = site + soup.form.attrs['action']
        page = read_as(opener.open(url, urllib.urlencode(data)))
        login_seq = write_html(Nomura401K.get_name(), page, login_seq)

        soup = bs(page, self.parser)
        frame = soup.findAll('frame', attrs={"name": 'contents'})[0]
        url = site + frame.attrs['src']
        page = read_as(opener.open(url))
        login_seq = write_html(Nomura401K.get_name(), page, login_seq)


        target = u'資産状況を詳しく見る'
        soup = bs(page, self.parser)
        l = [x for x in soup.find_all('a') if x.__unicode__().find(target) > 0]
        if len(l) == 0:
            raise ScrapError("{}:cannot find target link1 !!!".format(self.get_name()))
        else:
            url = site + l[0].attrs['href']
        page = read_as(opener.open(url))
        login_seq = write_html(Nomura401K.get_name(), page, login_seq)

        self.parse_performance_table(page,  adapter)

    def parse_performance_table(self, page, adapter):
        yen = u'円'

        def parse_page(page):
            soup = bs(page, self.parser)
            #find the table
            table = soup.body.findAll('div', attrs={"class": "m_money-table mt0"})[0].table
            rows = table.tbody.findAll('tr', recursive=False)
            #
            result = []
            for r in rows:
                a = r.a
                if a is None:
                    #valid fund detail has <a/>
                    break
                name = a.get_text()
                l = [x.get_text() for x in r.findAll('td',recursive=False) if x.get_text().find(yen) > 0]
                result.append((name, l))

            return result

        def parse_num_before_yen(s):
            s = strip_str(s)
            return get_digits(s[:s.find(yen)])

        p1 = parse_page(page)

        for p in p1:
            name = p[0]
            market_value = float(parse_num_before_yen(p[1][0]))

            s = p[1][0]
            amount = int(get_digits(s[s.find(yen):]))

            capital = float(get_digits(strip_str(p[1][1])))
            profit = float(get_digits(parse_num_before_yen(p[1][2])))
            price = float(get_digits(parse_num_before_yen(p[1][3])))

            adapter.onData(name, capital, amount, market_value, profit, price)

class Saison(Broker):
    def open(self, adapter):
        site = 'https://trade.saison-am.co.jp'
        url = site + '/webbroker3/0H/pc/WEB3AccountLogin.jsp'
        
        opener = self.build_url_opener()
        page = read_as(opener.open(url))
        login_seq = write_html(Saison.get_name(), page, 0)
        
        soup = bs(page, self.parser)
        f = soup.findAll('form',attrs={'name':'loginForm'})[0]
        data = parse_form_parameters(f)
        data['aa_accd'],data['lg_pw'] = adapter.get_login()
        
        url = site + f.attrs['action']
        
        page = read_as(opener.open(url,urllib.urlencode(data)))
        login_seq = write_html(Saison.get_name(), page, login_seq)
        
        soup = bs(page, self.parser)
        f=soup.findAll('form',attrs={'name':'forwardForm'})[0]
        data2 = parse_form_parameters(f)
        data.update(data2)
        url = site + f.attrs['action']

        page = read_as(opener.open(url,urllib.urlencode(data)))
        write_html(Saison.get_name(), page, login_seq)
        
        self.parse_performance_table(page, adapter)

    def parse_performance_table(self, page, adapter):
        yen = u'円'
        guchi = u'口'

        soup = bs(page, self.parser)
        t = soup.findAll('table',attrs={'class':'contents line'})[0]
        rows = t.findAll('tr', recursive=False)
        
        dataitem=5
        for r in rows[1:]:
            name = r.findAll('td',attrs={'class':'dataitem%02d start'%dataitem})[0].get_text()
            l = r.findAll('td',attrs={'class':'dataitem%02d end'%dataitem})
            dataitem += 1
            
            s = l[1].get_text()            
            amount = int(get_digits(s[:s.find(guchi)]))
            
            s = l[2].get_text()            
            price = float(get_digits(s[:s.find(yen)]))
            
            s = l[4].get_text()
            l = s.split('\n')
            market_value = float(get_digits(l[0]))
            profit = float(get_digits(l[1]))
            capital = market_value - profit
            
            adapter.onData(name, capital, amount, market_value, profit, price)


class Fidelity(Broker):
    class Perf:
        def __init__(self,a,px,v,p,c):
            self.amount  = a
            self.price   = px
            self.value   = v
            self.profit  = p
            self.capital = c
            
    def open(self, adapter):
        site = 'https://www.fidelity.jp'
        url = site + '/fskk/my-page/default.page'
        opener = self.build_url_opener()

        account, passwd = adapter.get_login()
        
        #parase the hidden parameters from form

        page = read_as(opener.open(url),'utf-8')
        login_seq = write_html(Fidelity.get_name(), page, 0 ,'utf-8')
        
        soup = bs(page, self.parser)
        f = soup.findAll('form',attrs={'name':'form1324881444971'})
        if len(f)==0:
            logging.error('Cannot find Fidelity login form!')
            return

        data = parse_form_parameters(f[0])
        data['loginVO.accountId']=account
        data['loginVO.password']=passwd
        data['x']='46'
        data['y']='30'

        url = site + f[0]['action']
        page = read_as(opener.open(url,urllib.urlencode(data)),'utf-8')
        login_seq = write_html(Fidelity.get_name(), page, login_seq ,'utf-8')
        
        soup = bs(page, self.parser)
        l = [ n['href'] for n in soup.find_all('a') if n.has_attr('title') and n['title']==u'お預り明細・ファンド積立（SBS）']
        if len(l) == 0:
            logging.error('Cannot find Fidelity balance page !')
            return

        url = site + l[0]
        page = read_as(opener.open(url),'utf-8')
        login_seq = write_html(Fidelity.get_name(), page, login_seq ,'utf-8')
        
        soup = bs(page)
        f=soup.findAll('table',attrs={'class':'ofTableStyle1 ofFont12'})
        if len(f) == 0:
            logging.error("Cannot find Fidelity asset table !")
            return
        
        a=f[0].find_all('tbody')
        if len(a) == 0:
            logging.error("Cannot find Fidelity asset tbody !")
            return

        #could have same product in different accounts, so group the performance by product
        perf = {}

        rows = a[0].find_all('tr')
        for r in rows:
            c = r.find_all('td')
            if len(c)<5:
                logging.error("Too few columns in Fidelity asset tbody!")
                return

            a = c[0].find_all('a')
            if len(a) == 0:
                continue #breakdown of NISA tenor

            name   = a[0].text
            price  = float(get_digits(c[1].text.split()[0]))
            amount = int(get_digits(c[2].text.split()[0]))
            capital = float(get_digits(c[3].text.split()[0]))*amount/10000
            value   = float(get_digits(c[4].text.split()[0]))
            profit  = value-capital
                
            if name in perf:
                p = perf[name]
                p.amount  += amount
                p.capital += capital
                p.value   += value
                p.profit  += profit
            else:
                perf[name] = Fidelity.Perf(amount,price,value,profit,capital)
            
        for k in perf.keys():
            p = perf[k]
            adapter.onData(k, p.capital, p.amount, p.value, p.profit, p.price)
        
        
class Monex(Broker):
    """
    Login to google finance portofolio
    """
    def open(self,adapter):
        url = 'https://accounts.google.com/ServiceLogin'
        
        opener = self.build_url_opener()

        p = read_as(opener.open(url),'utf8')
        seq = write_html(Monex.get_name(), p, 0)        
        soup = bs(p,self.parser)
        #f = soup.findAll('form',attrs={'name':'gaia_loginform'})[0]
        f = soup.form
        
        data = parse_form_parameters(f,'utf8')

        data['Email'],data['Passwd']=adapter.get_login()
        url='https://accounts.google.com/ServiceLoginAuth'
        p = read_as(opener.open(url, urllib.urlencode(data)),'utf8')
        seq = write_html(Monex.get_name(), p, seq)

        # The transaction CSV
        url = 'https://www.google.com/finance/portfolio?pid=1&output=csv&action=viewt&ei=OKZAVvHOH8aO0gTy_rDABw'
        p = read_as(opener.open(url),'utf8')
        c = csv.reader(p.split(u'\n')[1:])
        for fields in c:
            if fields is not None and len(fields)>2 and len(fields[0])>0:
                if not adapter.onTransaction(fields[0],fields[2].upper(),datetime.strptime(fields[3],'%b %d, %Y'),fields[4],fields[5],fields[7]):
                    break
            else:
                break

class FinancialData(Broker):
    """
    Download historical financial data from public site
    """
    def __init__(self,caption,start,end,proxy_handler=None):
        """
        start - start date
        end   - end date
        """
        self.start = start
        self.end   = end
        Broker.__init__(self,proxy_handler)
        print caption

        
class Xccy(FinancialData):
    """
    Download currency exchange rates
    """
    def open(self,adapter):
        def download(currency,dt,seq,adapter):
            opener = self.build_url_opener()
            url_formatted = url.format(currency,d.strftime("%Y-%m-%d"))
            #print url_formatted
            p = read_as(opener.open(url_formatted),'utf8')            
            seq = write_html(currency, p, seq,'utf8')

            soup = bs(p,self.parser)
            t = soup.findAll('table',attrs={'id':'historicalRateTbl'})[0]

            rows = t.find_all('tr')
            for r in rows[2:]:
                cols = r.find_all('td')
                if cols[0].get_text() == u'JPY':
                    adapter.onXccy(dt,currency,'JPY',float(get_digits(cols[2].get_text())))
            
            return seq


        url = "http://www.xe.com/currencytables/?from={}&date={}"
        d = self.start
        seq = 0
        while  d <= self.end:
            try:
                print("Downloading Xccy :{}".format(d))
                seq = download('USD', d, seq, adapter)
                seq = download('CNY', d, seq, adapter)
            except:
                print "Failed to download Xccy for {}".format(d)
            d = d + timedelta(1)

class Yahoo(FinancialData):
    """
    Download historical quotes of stocks/ETFs from Yahoo finance
    """
    def __init__(self,symbol,start,end,proxy_handler=None):
        self.symbol = symbol
        FinancialData.__init__(self,symbol,start,end,proxy_handler)

    def open(self,adapter):
        # URL paramters :
        # s - symbol, a/d - start/end month (00~11), b/e - start/end day, c/f - start/end year
        # g=?  d-daily v-dividend only
        url = 'http://real-chart.finance.yahoo.com/table.csv?s=%s&a=%02d&b=%02d&c=%04d&d=%02d&e=%02d&f=%04d&g=%s&ignore=.csv'%(self.symbol,self.start.month-1,self.start.day,self.start.year,self.end.month-1,self.end.day,self.end.year,'d')
        #print url
        try:
            opener = self.build_url_opener()
            p = read_as(opener.open(url),'utf8')
            #print p
            c = csv.reader(p.split(u'\n')[1:])
            #print c
            for f in c:
                #print f
                if f is not None and len(f)>4:
                    if not adapter.onQuote(self.symbol,datetime.strptime(f[0],'%Y-%m-%d'),float(f[4])):
                        break
        except urllib2.HTTPError:
            print "Failed to open %s"%url
            
    def __unicode__(self):
        return self.symbol

if __name__ == '__main__':
    """
    parameter : 
        -fxxxxxx  path to sqlite db file xxxxx
        one or more broker type, or all brokers if no parameter given
    """
    import sys
    from adapter import SqliteAdapter
    from scraper import *
    from utils import cmdline_args
    from config import BROKERS
    from adapter import ConsoleAdapter,SqliteAdapter


    def do_work(db,broker):
        if db is None:
            adapter = ConsoleAdapter(broker.get_name())
        else:
            adapter = SqliteAdapter(db,broker.get_name())
        broker.open(adapter)
        adapter.close()
        
    proxy = None
    args,brokers = cmdline_args(sys.argv[1:])


    db = args['dbfile']
    
    if len(brokers) == 0:
        for broker in [getattr(sys.modules[__name__], x)(proxy) for x in BROKERS]:
            do_work(db,broker)
    else:
        for broker_name in brokers:
            broker_class = getattr(sys.modules[__name__], broker_name)
            do_work(db,broker_class(proxy))

