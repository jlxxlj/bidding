# coding=utf-8
# author="Jianghua Zhao"


"""
对招投标公告文档进行解析，提取其中有用信息
"""

from announce_analysis import *
from config.config import *
from announce_analysis_result_save import save_bidding_result
import json
reload(sys)
sys.setdefaultencoding('utf-8')
logger = get_logger(__file__)

Contne = '''

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" >
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>青海省招标投标网 ·
        国采（青海）招标有限公司关于青海省重点污染源自动监控设备运营维护单位招标项目预中标公示
    </title>
    <meta content="青海省招标投标网 国采（青海）招标有限公司关于青海省重点污染源自动监控设备运营维护单位招标项目预中标公示"
        name="keywords" />
    <meta name="GENERATOR" content="Microsoft Visual Studio .NET 7.1" />
    <meta name="ProgId" content="VisualStudio.HTML" />
    <meta name="Originator" content="Microsoft Visual Studio .NET 7.1" />
    <meta http-equiv="Content-Type" content="text/html; charset=gb2312" />
    <link href="/qhweb/Template/Default/css/style.css" type="text/css" rel="stylesheet" />
    <script type="text/javascript">
        function ResizeToScreen(div, pX, pY) {

            document.getElementById(div).style.display = "";
            var _w = (screen.availWidth - 990) / 2
            document.all(div).style.pixelLeft = parseInt(pX) + _w; //这个地址不知道咋算呢
            document.all(div).style.pixelTop = parseInt(pY) + 460;
            document.body.scrollTop = pY - 200; //调整用
        }

    </script>
</head>
<body>
    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" class="table_width">
      <tr>
        <td><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
    <head>
    <title>青海省招标投标网</title>
    <meta name="GENERATOR" content="Microsoft Visual Studio .NET 7.1" />
    <meta name="ProgId" content="VisualStudio.HTML" />
    <meta name="Originator" content="Microsoft Visual Studio .NET 7.1" />
    <meta http-equiv="Content-Type" content="text/html; charset=gb2312" />
    <link href="/qhweb/Template/Default/css/style.css" type="text/css" rel="stylesheet" />
    <link type="text/css" href="/qhweb/Template/Default/css/menu.css" rel="stylesheet" />
    <link rel="stylesheet" href="/qhweb/Template/Default/css/common.css">
    <link rel="stylesheet" href="/qhweb/Template/Default/css/head.css">
    <script src="/qhweb/Template/Default/js/jquery-1.11.0.min.js"></script>
    <script type="text/javascript" src="/qhweb/Template/Default/javascript/js.js"></script>
    <script language="javascript" type="text/javascript">
        function ChangeTab2(number, TdID, DivID, Tablen, classid) {
            var len = Tablen
            var controlID = TdID + number;

            for (var i = 1; i < len; i++) {
                controlID = TdID + i;
                document.getElementById(controlID).className = "OutFont" + classid;
                controlID = DivID + i;
                document.getElementById(controlID).style.display = "none";
            }
            controlID = TdID + number;
            document.getElementById(controlID).className = "OverFont" + classid;
            controlID = DivID + number;
            document.getElementById(controlID).style.display = "";
        }

        function show(idx) {
            document.getElementById('xianshi' + idx).style.display = '';
        }
        function hide(idx) {
            document.getElementById('xianshi' + idx).style.display = 'none';
        }
    </script>
    <script>
        function winopen(url) {
            top.location = url;
        }
        function winopennew(url) {
            window.open(url);
        }
    </script>
    <script type="text/javascript">

        function gettime() {
            today = new Date();

            var d = new initArray("星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六");
            document.write("<span>" + today.getFullYear(), "年", today.getMonth() + 1, "月", today.getDate(), "日&nbsp;&nbsp;", d[today.getDay() + 1] + "</span>");  //-->
        }
        function initArray() {
            this.length = initArray.arguments.length
            for (var i = 0; i < this.length; i++)
                this[i + 1] = initArray.arguments[i]
        }


        function OpenWin2(Url) {
            window.open(Url, "_top");
        }
        function OpenWin(Url) {

            window.open(Url, '', 'Width=530,Height=565,help:no,status:no,scrollbars=yes,resizable=yes');
        }
        
    </script>
    <script type="text/javascript">
        $(function () {
            $("#nav>li").hover(function () {
                $(this).children('ul').stop().slideDown(300);
                $(this).css("background", "url(/fx_front/template/default/images/nav_hover.jpg) bottom no-repeat");
                $(this).children('a').css("color", "#383838")
            },
		function () {
		    $(this).children('ul').stop().hide(100);
		    $(this).css("background", "");
		    $(this).children('a').css("color", "")
		}
		)
        })

    </script>
    </head>
    <body ms_positioning="GridLayout">
<table  class="table_width">
      <tr>
    <td width="1016" height="200" align="center" background="/qhweb/Template/Default/images/top_bg01.jpg" style="background-repeat:no-repeat; background-position:top left"><img src="/qhweb/Template/Default/images/header_bg.png" alt="青海省招标投标网"/></td>
  </tr>
      <tr>
    <td width="1016" align="center" background="/qhweb/Template/Default/images/bj_77.jpg">
       <table width="991" height="34" border="0" align="center" cellpadding="0" cellspacing="0">
        <tr>
          <td width="3" background="/qhweb/Template/Default/images/nav_06.jpg" style="background-repeat:no-repeat"></td>
          <td width="985" background="/qhweb/Template/Default/images/navbj_08.jpg" style="background-repeat:repeat-x">
          <ul id="nav">
              <li style="padding-left:16px" ><a target="_top" href="/qhweb/Template/Default/../../"><span class="bold">首页</span></a></li>
              <li class="sppic"></li>
              <li> <a target="_top" href="/qhweb/Template/Default/../../bszn" class="parent"><span class="bold">办事指南</span></a></li>
              <li class="sppic"></li>
              <li> <a href="/qhweb/Template/Default/../../jyxx" target="_parent" class="parent"><span class="bold">交易信息</span></a>
                <ul>
                  <li><a href="/qhweb/Template/Default/../../jyxx/005001" target="_parent">工程建设</a></li>
                  <li><a href="/qhweb/Template/Default/../../jyxx/005002" target="_parent">政府采购</a></li>
                  <li><a href="/qhweb/Template/Default/../../jyxx/005004" target="_parent">产权交易</a></li>
                  <li><a href="/qhweb/Template/Default/../../jyxx/005003" target="_parent">矿产权交易</a></li>
                  <li><a href="/qhweb/Template/Default/../../jyxx/005005" target="_parent">药品采购</a></li>
                  <li class="list_btm"></li>
                </ul>
              </li>
              <li class="sppic"></li>
              <li><a target="_top" href="/qhweb/Template/Default/../../xypt" class="parent"><span class="bold">信用平台</span></a>
                <ul>
                  <li><a href="/qhweb/Template/Default/../../xypt/006001" target="_parent">光荣榜</a></li>
                  <li><a href="/qhweb/Template/Default/../../xypt/006002" target="_parent">曝光台</a></li>
                  <li><a href="/qhweb/Template/Default/../../xypt/006003" target="_parent">不良行为记录</a></li>
                  <li class="list_btm"></li>
                </ul>
              </li>
              <li class="sppic"></li>
              <li> <a target="_top" href="/qhweb/Template/Default/../../sjtj/default.aspx" class="parent"><span class="bold">数据统计</span></a></li>
              <li class="sppic"></li>
              <li> <a target="_top" href="/qhweb/Template/Default/../../ptjs" class="parent"><span class="bold">平台介绍</span></a></li>
              <li class="sppic"></li>
              <li> <a target="_top" href="/qhweb/Template/Default/../../customqyinfo/qyinfo.aspx"><span class="bold">诚信库查询</span></a> </li>
              <li style="display:none" class="sppic"></li>
              <li style="display:none"> <a target="_top" href="/qhweb/Template/Default/../../ztbxh/015001"><span class="bold">招投标协会</span></a> </li>
              <li class="sppic"></li>
              <li> <a target="_top" href="javascript:void(0);" class="parent"><span class="bold">站点切换</span></a>
                <ul >
                           <li> <a href="http://www.xnggzy.gov.cn/xnweb/" target="_blank" title="西宁市">西宁市</a> </li>
                           <li> <a href="http://qhzbtb.qhwszwdt.gov.cn/qhweb/" target="_blank" title="海东市">海东市</span> </a> </li>
                           <li> <a href="http://xzzx.haixi.gov.cn/hxggzyweb/" target="_blank" title="海西州">海西州</a> </li>
                           <li> <a href="http://125.72.23.19:90/hnztb/" target="_blank" title="海南州">海南州</a> </li>
                           <li> <a href="http://www.hbzwzx.gov.cn/Front/ggzyjy/" target="_blank" title="海北州">海北州</a> </li>
                           <li> <a href="http://xzfw.hnz.gov.cn/Front/ggzyjy/" target="_blank" title="黄南州">黄南州</a> </li>
                           <li> <a href="http://qhzbtb.qhwszwdt.gov.cn/qhweb/" target="_blank" title="果洛州">果洛州</a> </li>
                           <li> <a href="http://qhzbtb.qhwszwdt.gov.cn/qhweb/" target="_blank" title="玉树州">玉树州</a> </li>
                           <li> <a href="http://221.207.6.20:81/EpointWeb_Gem/default.aspx" target="_blank" title="格尔木">格尔木</a> </li>
                           <li class="list_btm"></li>
                        </ul>
              </li>
              <li class="sppic"></li>
              <li> <a target="_top" href="http://www.qhwszwdt.gov.cn/Front/default.aspx"><span class="bold">返回中心</span></a> </li>
			  <li class="sppic"></li>
			  <li> <a target="_top" href="http://111.44.251.34"><span class="bold" style="color:red" >新版系统</span></a> </li>
            </ul></td>
          <td width="3" background="/qhweb/Template/Default/images/nav_12.jpg" style="background-repeat:no-repeat"></td>
        </tr>
      </table>
      </td>
  </tr>
      <tr ><td width="1016" align="center" background="/qhweb/Template/Default/images/bj_77.jpg">
    <table width="991" height="37" border="0" align="center" cellpadding="0" cellspacing="0">
          <tr>
        <td width="3" background="/qhweb/Template/Default/images/float_13.jpg"></td>
        <td width="434" valign="bottom" background="/qhweb/Template/Default/images/fbj_15.jpg"><table width="100%" height="37" border="0" cellspacing="0" cellpadding="0">
            <tr>
              <td width="148" class="black"><script type="text/javascript">
						gettime();
					</script></td>
              <td width="5"></td>
              <td width="300"><iframe allowtransparency="true" frameborder="0" width="200" height="37" scrolling="no" src="http://tianqi.2345.com/plugin/widget/index.htm?s=3&z=2&t=0&v=0&d=3&bd=0&k=&f=&q=1&e=1&a=0&c=52866&w=200&h=37&align=center"></iframe></td>
            </tr>
          </table></td>
        <td width="551" background="/qhweb/Template/Default/images/bj_18.jpg"><table width="551" height="37" border="0" cellspacing="0" cellpadding="0">
            <tr>
              <td width="134" align="center"><a href="/qhweb/Template/Default/../../jyxx/005001" target="_top" class="black2">工程建设</a></td>
              <td width="86" align="center"><a href="/qhweb/Template/Default/../../jyxx/005002" target="_top" class="black2">政府采购</a></td>
              <td width="140" align="center"><a href="/qhweb/Template/Default/../../jyxx/005005" target="_top" class="black2">药品采购</a></td>
              <td width="93"><a href="/qhweb/Template/Default/../../jyxx/005004" target="_top" class="black2">产权交易</a></td>
              <td width="98" align="center"><a href="/qhweb/Template/Default/../../jyxx/005003" target="_top" class="black2">矿业权交易</a></td>
            </tr>
          </table></td>
        <td width="3" background="/qhweb/Template/Default/images/float_20.jpg"></td>
      </tr>
        </table>
    </td>
  </tr>
    </table>
<script src="/qhweb/Template/Default/js/index.js"></script>
</body>
</html>
</td>
      </tr>
    </table>
    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" class="table_width">
      <tr>
        <td background="/qhweb/Template/Default/images/bj_77.jpg" height="7"></td>
      </tr>
    </table>
    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" class="table_width">
      <tr>
        <td background="/qhweb/Template/Default/images/bj_77.jpg">
        <table width="991" height="100%" border="0" align="center" cellpadding="0" cellspacing="0">
          <tr>
            <td valign="top" height="30" background="/qhweb/Template/Default/images/more_2.gif"><table width="100%" border="0" cellpadding="0" cellspacing="0">
              <tr>
                <td width="25" height="30" background="/qhweb/Template/Default/images/more_1.jpg"></td>
                <td align="left" width="977"><table cellSpacing="0" cellPadding="0" border="0"><TR><TD align="center" width="15"></TD><TD align="left"><FONT color="#000000" class=currentpostionfont><b>您现在的位置：</b></FONT><A href='/qhweb/'><FONT color="#000000" class=currentpostionfont>首页</FONT></A><FONT color="#ce392c"> >> <a href='/qhweb/jyxx'><FONT color="#ce392c" class=currentpostionfont>交易信息</font></a> >> <a href='/qhweb/jyxx/005002'><FONT color="#ce392c" class=currentpostionfont>政府采购</font></a> >> <a href='/qhweb/jyxx/005002/005002004'><FONT color="#ce392c" class=currentpostionfont>中标公示</font></a></FONT></TD></TR></table></td>
              </tr>
            </table></td>
          </tr>
          <tr>
            <td align="center" valign="top" bgcolor="#ffffff" style="padding-left: 30px; padding-right: 30px;
                padding-top: 30px; border-bottom-style: none; border-top-style: none"><!--正文开始-->
              
              <table id="tblInfo" cellspacing="1" cellpadding="1" width="931" align="center" border="0"
                    runat="server">
                <tr>
                  <td id="tdTitle" align="center" runat="server"><font color=""
                                style="font-size: 25px"> <b>
                    国采（青海）招标有限公司关于青海省重点污染源自动监控设备运营维护单位招标项目预中标公示
                    </b></font> <br />
                    <br />
                    
									</td>
                </tr>
				<tr>
                  <td height="30" style="background-color:#efefef" align="center"><font color="#888888" class="webfont">【信息时间：
                      2014/5/14 9:05:55
                      &nbsp;&nbsp;阅读次数：
                      <script src="/qhweb/Upclicktimes.aspx?InfoID=a9609b98-f35a-490f-8177-c7e6d49114b1"></script>
                      】<a href="javascript:void(0)" onClick="window.print();"><font color="#000000" class="webfont">【我要打印】</font></a><a
                                    href="javascript:window.close()"><font color="#000000" class="webfont">【关闭】</font></a></font><font color="#000000">
                        
                      </font></td>
                </tr>
                <tr>
                  <td height="10"></td>
                </tr>
                <tr>
                  <td height="250" valign="top" class="infodetail" id="TDContent"><div>
                    <!--EpointContent-->
                    <p class="ParagraphIndent"><span style="font-size: 18px"><span style="font-family: 宋体">&nbsp; </span></span></p>
<div class="MsoNormal" style="line-height: 200%; text-indent: 24pt; mso-char-indent-count: 2.0"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">国采（青海）招标有</span><span style="line-height: 200%; mso-font-kerning: 0pt; mso-bidi-font-family: 宋体">限公司受青海省环境监察总队委</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">托，就青海省重点污染源自动监控设备运营维护单位招标项目进行公开招标，按法定程序进行了开标、评标、定标，现就本次招标的结果公示如下：</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoListParagraph" style="line-height: 200%; text-indent: 0cm; mso-char-indent-count: 0"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">一、招标项目名称：青海省重点污染源自动监控设备运营维护单位招标项目</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%; mso-font-width: 86%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoListParagraph" style="line-height: 200%; text-indent: 24pt"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">标书编号：</span><span lang="EN-US" style="line-height: 200%">GC</span><span style="line-height: 200%">（<span lang="EN-US">QH</span>）<span lang="EN-US">GZ-FW-2014-001</span></span></span></span><span lang="EN-US" style="font-size: 12pt; font-family: 宋体; line-height: 200%; mso-hansi-font-family: 'Times New Roman'"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoListParagraph" style="margin-left: 24pt; line-height: 200%; text-indent: -24pt; mso-char-indent-count: 0; mso-list: l0 level1 lfo1; tab-stops: list 24.0pt"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%; mso-bidi-font-family: 宋体"><span style="mso-list: Ignore">二、</span></span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">采购项目内容、数量</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="line-height: 200%; text-indent: 24pt; mso-char-indent-count: 2.0"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">随着全省工业化进程的加快，污染源自动监控设施建设的长足发展，污染源自动监控设施数量由</span><span lang="EN-US" style="line-height: 200%">2010</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">年的</span><span lang="EN-US" style="line-height: 200%">80</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">台（套）增加到现在的</span><span lang="EN-US" style="line-height: 200%">325</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">台（套）。根据《污染源自动监控设施运行管理办法》要求，我省结合重点污染源数量少、分布广的实际，在原有运营单位不变的基础上，再招标三家第三方运营污染治理设施单位，对全省污染源自动监控设施进行统一运营，形成竞争机制。</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="line-height: 200%"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">三、评标信息</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin-left: 21.2pt; line-height: 200%; mso-para-margin-left: 2.02gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">1</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">、招标公告发布媒体及日期：青海省政府采购信息网</span><span lang="EN-US" style="line-height: 200%">2014</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">年</span><span lang="EN-US" style="line-height: 200%">4</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">月</span><span lang="EN-US" style="line-height: 200%">21</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">日</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin-left: 21.2pt; line-height: 200%; mso-para-margin-left: 2.02gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">2</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">、评标日期：</span><span lang="EN-US" style="line-height: 200%">2014</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">年</span><span lang="EN-US" style="line-height: 200%">5</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">月</span><span lang="EN-US" style="line-height: 200%">13</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">日</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin-left: 21.2pt; line-height: 200%; mso-para-margin-left: 2.02gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">3</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">、评标地点：国采（青海）招标有限公司</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin-left: 21.2pt; line-height: 200%; mso-para-margin-left: 2.02gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">4</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">、定标日期：</span><span lang="EN-US" style="line-height: 200%">2014</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">年</span><span lang="EN-US" style="line-height: 200%">5</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">月</span><span lang="EN-US" style="line-height: 200%">13</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">日</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin-left: 21.2pt; line-height: 200%; mso-para-margin-left: 2.02gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">5</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">、评标委员会名单：</span><span style="line-height: 200%; mso-font-kerning: 0pt; mso-bidi-font-family: 宋体">樊文辉、李萍、周少红、李得恩</span><span style="line-height: 200%">、</span><span style="line-height: 200%; mso-font-kerning: 0pt; mso-bidi-font-family: 宋体">余全盛（</span><span style="color: black; line-height: 200%">业主代表）。</span></span></span><span style="font-size: 12pt; font-family: 宋体; color: black; line-height: 200%"><span lang="EN-US"><o:p class="ParagraphIndent"></o:p></span></span></div>
<div class="MsoNormal" style="line-height: 200%"><strong><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">四、中标信息</span></span></span></strong><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="line-height: 200%; text-indent: 24pt; mso-char-indent-count: 2.0"><strong><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">本次招标项目预中标单位：聚光科技（杭州）股份有限公司、青海天普伟业环保科技有限公司、北京雪迪龙科技股份有限公司。</span></span></span></strong><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="line-height: 200%"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">五、本次招标联系事项</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin-left: 21pt; line-height: 200%"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">1</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">、采购单位：青</span><span style="line-height: 200%">海省环境监察总队</span></span></span><span style="font-size: 12pt; font-family: 宋体; line-height: 200%"><span lang="EN-US"><o:p class="ParagraphIndent"></o:p></span></span></div>
<div class="MsoNormal" style="margin-left: 21pt; line-height: 200%; text-indent: 18pt; mso-char-indent-count: 1.5; mso-para-margin-left: 2.0gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%">联系人：朱老师<span lang="EN-US"><span style="mso-spacerun: yes">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </span></span>联系电话：<span lang="EN-US">0971-8185797</span></span></span></span><span style="font-size: 12pt; font-family: 宋体; line-height: 200%"><span lang="EN-US"><o:p class="ParagraphIndent"></o:p></span></span></div>
<div class="MsoNormal" style="margin-left: 21pt; line-height: 200%"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">2</span><span style="line-height: 200%">、招标代理机构：国采（青海）招标有限公司</span></span></span><span style="font-size: 12pt; font-family: 宋体; line-height: 200%"><span lang="EN-US"><o:p class="ParagraphIndent"></o:p></span></span></div>
<div class="MsoNormal" style="margin-left: 21pt; line-height: 200%; text-indent: 18pt; mso-char-indent-count: 1.5; mso-para-margin-left: 2.0gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">联系人：</span></span></span><span style="font-size: 12pt; font-family: 宋体; line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'"><st1:personname w:st="on" productid="张"><span style="font-size: 18px"><span style="font-family: 宋体">张</span></span></st1:personname></span><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">女士</span><span lang="EN-US" style="line-height: 200%"><span style="mso-spacerun: yes">&nbsp;&nbsp; </span><span style="mso-spacerun: yes">&nbsp;&nbsp;&nbsp;</span><span style="mso-spacerun: yes">&nbsp;&nbsp;&nbsp;</span><span style="mso-spacerun: yes">&nbsp;</span><span style="mso-spacerun: yes">&nbsp;</span></span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">联系电话：</span><span lang="EN-US" style="line-height: 200%">0971-6278764</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="margin: 7.8pt 0cm; line-height: 200%; text-indent: 24pt; mso-char-indent-count: 2.0; mso-para-margin-left: 0cm; mso-para-margin-top: .5gd; mso-para-margin-right: 0cm; mso-para-margin-bottom: .5gd"><span style="font-size: 18px"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">各有关当事人对中标结果有异议的，可在中标公示发布之日起七个工作日内，以书面形式向国采（青海）招标有限公司提出质疑，逾期将不再受理。</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="line-height: 200%"><span style="font-family: 宋体"><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"><span style="font-size: 18px">&nbsp;</span></o:p></span></span></div>
<p><span style="font-size: 18px">
<div class="MsoNormal" style="line-height: 200%"><span lang="EN-US" style="line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="text-align: right; line-height: 200%" align="right"><span style="font-family: 宋体"><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">国采（青海）招标有限公司</span></span></div>
</span></p>
<div class="MsoNormal" style="text-align: right; line-height: 200%" align="right"><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
<div class="MsoNormal" style="text-align: right; line-height: 200%; margin-right: 22pt" align="right"><span style="font-size: 18px"><span style="font-family: 宋体"><span lang="EN-US" style="line-height: 200%">2014</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">年</span><span lang="EN-US" style="line-height: 200%">5</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">月</span><span lang="EN-US" style="line-height: 200%">14</span><span style="line-height: 200%; mso-ascii-font-family: 'Times New Roman'; mso-hansi-font-family: 'Times New Roman'">日</span></span></span><span lang="EN-US" style="font-size: 12pt; line-height: 200%"><o:p class="ParagraphIndent"></o:p></span></div>
                    <!--EpointContent-->
                  </div>
                   </td>
                </tr>
                <tr>
                  <td align="right">
                    <br>
                    </td>
                </tr>
                <tr id="trAttach" runat="server">
                  <td><table id="filedown" cellspacing="1" cellpadding="1" width="100%" border="0" runat="server">
                    <tr>
                      <td valign="top" style="font-size: medium;"><b>
                        
                      </b></td>
                    </tr>
                  </table></td>
                </tr>
                <tr>
                  <td></td>
                </tr>
                <tr>
                  <td height="30"></td>
                </tr>
                
                
              </table>
              <!--正文结束--></td>
          </tr>
        </table></td>
      </tr>
    </table>
    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" class="table_width">
      <tr>
        <td><iframe src="/qhweb/Template/Default/pagefoot.htm" width="100%" height="114" frameborder="0" scrolling="no"></iframe></td>
      </tr>
</table>
</body>
</html>

'''

def test():
    # with open("test/test_data_0") as f:
    #     content = "".join(f.readlines())
    #     bidding_item = {"content": Contne}
    #     res = analysis(bidding_item)
    #     print json.dumps(res,indent=2,ensure_ascii=False)
        # save_bidding_result(json.dumps(res))


    # with open("test/.json") as f:
    #     item = json.load(f)
    #     res = analysis(item)
    #     print res
    #     save_bidding_result(json.dumps(res))

    # import os
    #
    # folder = "test/ccgp"
    # names = os.listdir(folder)
    # for name in names:
    #     if name.startswith("."):
    #         continue
    #     # if "376668591300505600" not in name:
    #     #     continue
    #     file_path = os.path.join(folder, name)
    #     with open(file_path) as f:
    #         item = json.load(f)
    #         print item[URL]
    #         res = analysis(item)
    #
    #         # save_bidding_result(json.dumps(res))

    # 验证object_key
    # region_code = u"|".join(BID_REGION_CODE_TABLE.values())
    # reg_key = re.compile(u"^source/(?:%s)/.*/\d{4}/\d{1,2}/\d{1,2}/.*\.json" % region_code)
    import boto3
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION_NAME)
    s3 = aws_s3_sc.S3Util()
    #
    obj_key = "source/guang_xi/www.gxzfcg.gov.cn/2017/02/28/http%3A%2F%2Fwww.gxzfcg.gov.cn%2Fview%2Fstaticpags%2Fsxjcg_zbgg%2F8ab8a0925a4f0526015a83b36c1a0fe6.html.json"
    obj_data = s3.select(table="bidding", condition={}, file_name=obj_key)
    obj_data = json.load(obj_data["Body"])
    res = analysis(obj_data)
    content_source = "s3:bidding:" + obj_key
    announce_analysis_result_save(res, content_source)

    paginator = client.get_paginator('list_objects')
    result = paginator.paginate(Bucket='bidding', Prefix="source/chong_qing/www.cqggzy.com/2017/04/24")

    count = 0
    for pag in result:
        for item in pag.get("Contents", []):
            count += 1

            obj_key = item["Key"]
            if not reg_key.search(obj_key):
                continue
            obj_data = s3.select(table="bidding", condition={}, file_name=obj_key)
            obj_data = json.load(obj_data["Body"])
            print "\n", obj_key

            # 分析数据
            try:
                announce_data = analysis(obj_data)
            except Exception as e:
                logger.exception(e)
                new_name = "parse_error/" + urllib.urlencode({"name": obj_key})[5:]
                s3.insert(table="bidding", data=obj_data, file_name=new_name)
                continue
            # 存库
            content_source = "s3:bidding:" + obj_key
            announce_analysis_result_save(announce_data, content_source)
        if count > 100:
            break


if __name__ == "__main__":
    test()
