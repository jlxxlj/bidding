# coding=utf-8
# author="Jianghua Zhao"

# 设置work_mem
set_work_mem_32m_non_query = "SET work_mem='32MB';"
set_work_mem_default_non_query = "SET work_mem=default;"

# 全国各个省直辖市中标数及中标总金额
nation_amount_count_base_on_province_query = """
        SELECT announce.province AS province, SUM(announce.amount) AS amount, COUNT(*) AS count
        FROM bidding_announce announce
        WHERE announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND announce.province IS NOT NULL
        AND NOT announce.amount>=200000000
        AND announce.status<2
        {user_constrain}
        GROUP BY announce.province
        ORDER BY amount DESC;
    """

# 省下各个市中标数及中标总金额
province_amount_count_base_on_city_query = """
        SELECT announce.city AS city, SUM(announce.amount) AS amount, COUNT(*) AS count
        FROM bidding_announce announce
        WHERE announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        {user_constrain}
        GROUP BY announce.city
        ORDER BY amount DESC;
    """

# 直辖市下各个区县中标数及中标总金额
province_amount_count_base_on_county_query = """
        SELECT announce.county AS county, SUM(announce.amount) AS amount, COUNT(*) AS count
        FROM bidding_announce announce
        WHERE announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        {user_constrain}
        GROUP BY announce.county
        ORDER BY amount DESC;
    """

# 每天中标数及中标总金额
amount_count_base_on_date_query = """
        SELECT to_char(announce.published_ts, 'YYYY-MM-DD') as "publishDay", SUM(announce.amount) AS amount, COUNT(*) AS count
        FROM bidding_announce announce
        WHERE announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        {user_constrain}
        GROUP BY "publishDay"
        ORDER BY "publishDay" DESC ;
    """

# 中标总金额top-n的采购人
top_n_amount_base_on_purchaser_query = """
        SELECT announce.purchaser AS purchaser, SUM(announce.amount) AS amount
        FROM bidding_announce announce
        WHERE announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        AND announce.purchaser IS NOT NULL
        {user_constrain}
        GROUP BY purchaser
        ORDER BY amount DESC
        LIMIT %(top_n)s;
    """

# 中标总金额top-n的采购代理人
top_n_amount_base_on_agent_query = """
        SELECT announce.purchase_agent AS agent, SUM(announce.amount) AS amount
        FROM bidding_announce announce
        WHERE announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        AND announce.purchase_agent IS NOT NULL
        {user_constrain}
        GROUP BY agent
        ORDER BY amount DESC
        LIMIT %(top_n)s;
    """

# 中标总金额top-n的中标人
top_n_amount_base_on_winner_query = """
        SELECT result.winning_company AS winner, SUM(result.winning_amount) AS amount
        FROM bidding_announce announce, bidding_result result
        WHERE announce.id=result.bidding_announce_id
        AND announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        AND result.winning_amount<100000000
        AND result.unit='元'
        AND result.currency='人民币'
        AND result.role_type='winner'
        {user_constrain}
        GROUP BY winner
        ORDER BY amount DESC
        LIMIT %(top_n)s;
    """

# 中标人信息
winner_info_query = """
        SELECT
            announce.id as "announceID",
            announce.purchase_agent as "agent",
            announce.agent_contact_phone as "agentContactPhone",
            announce.purchaser as "purchaser",
            announce.purchaser_contact_phone as "purchaserContactPhone",
            announce.announce_type as "announceType",
            to_char(announce.published_ts, 'yyyy-mm-dd') as "publishedDate",
            announce.province as "province",
            announce.city as "city",
            announce.county as "county",
            announce.title as "title",
            announce.url as "url",
            result.winning_company as "winningCompany",
            result.winning_amount as "amount",
            result.unit as "unit",
            result.currency as "currency",
            result.role_name as "roleName"
        FROM bidding_announce announce, bidding_result result
        WHERE announce.id=result.bidding_announce_id
        AND announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        AND NOT result.winning_amount>=500000000
        AND result.role_type='winner'
        {user_constrain}
        ORDER BY "publishedDate" DESC, "announceID" DESC
        LIMIT %(page_size)s
        OFFSET %(skip_n)s;
"""

# 中标人信息总量统计
winner_info_count_query = """
        SELECT
            count(*) as "count"
        FROM bidding_announce announce, bidding_result result
        WHERE announce.id=result.bidding_announce_id
        AND announce.published_ts >= %(start_date)s
        AND announce.published_ts <= %(end_date)s
        AND NOT announce.amount>=200000000
        AND announce.status<2
        AND NOT result.winning_amount>=500000000
        AND result.role_type='winner'
        {user_constrain};
"""

# 公司中标信息查询
company_bidding_info_query = """
        select distinct
               announce.id as "announceID",
               result.id as "resultID",
               result.winning_company as "winningCompany",
               result.winning_amount as "winningAmount",
               result.unit as "unit",
               result.currency as "currency",
               result.role_name as "roleName",
               result.candidate_rank as "candidateRank",
               result.segment_name as "segmentName",
               result.role_type as "roleType",
               announce.purchaser as "purchaser",
               announce.purchase_agent as "purchaseAgent",
               announce.purchase_category as "purchaseCategory",
               announce.title as "title",
               announce.url as "url",
               announce.content_source as "contentSource",
               announce.website as "website",
               announce.province as "province",
               announce.city as "city",
               announce.county as "county",
               to_char(announce.published_ts, 'yyyy-mm-dd HH:MM:SS') as "publishedDateTime",
               to_char(announce.announced_ts, 'yyyy-mm-dd') as "announcedDate",
               to_char(announce.winning_ts, 'yyyy-mm-dd') as "winningDate",
               announce.announce_type as "announceType",
               announce.amount as "totalAmount",
               announce.unit as "totalAmountUnit",
               announce.currency as "totalAmountCurrency"
        from bidding_result result, bidding_announce announce
        where result.bidding_announce_id = announce.id
        and announce.id in (
              SELECT bidding_announce_id
              FROM bidding_result br
              WHERE br.winning_company=%s
            )
        and announce.published_ts >=%s
        and announce.published_ts <=%s
        and announce.status < 2
        and announce.content_source is not null
        order by to_char(announce.published_ts, 'yyyy-mm-dd HH:MM:SS') desc, announce.id ASC ;
"""

# 公司中标信息查询by id
company_bidding_info_by_id_query = """
        select
               announce.id as "announceID",
               result.id as "resultID",
               result.winning_company as "winningCompany",
               result.winning_amount as "winningAmount",
               result.unit as "unit",
               result.currency as "currency",
               result.role_name as "roleName",
               result.candidate_rank as "candidateRank",
               result.segment_name as "segmentName",
               result.role_type as "roleType",
               announce.purchaser as "purchaser",
               announce.purchase_agent as "purchaseAgent",
               announce.purchase_category as "purchaseCategory",
               announce.title as "title",
               announce.url as "url",
               announce.content_source as "contentSource",
               announce.website as "website",
               announce.province as "province",
               announce.city as "city",
               announce.county as "county",
               to_char(announce.published_ts, 'yyyy-mm-dd HH:MM:SS') as "publishedDateTime",
               to_char(announce.announced_ts, 'yyyy-mm-dd') as "announcedDate",
               to_char(announce.winning_ts, 'yyyy-mm-dd') as "winningDate",
               announce.announce_type as "announceType",
               announce.amount as "totalAmount",
               announce.unit as "totalAmountUnit",
               announce.currency as "totalAmountCurrency"
        from bidding_result result, bidding_announce announce
        where result.bidding_announce_id = announce.id
        and announce.id=%s;
"""

# 公司中标信息查询by url
company_bidding_info_by_url_query = """
        select
               announce.id as "announceID",
               result.id as "resultID",
               result.winning_company as "winningCompany",
               result.winning_amount as "winningAmount",
               result.unit as "unit",
               result.currency as "currency",
               result.role_name as "roleName",
               result.candidate_rank as "candidateRank",
               result.segment_name as "segmentName",
               result.role_type as "roleType",
               announce.purchaser as "purchaser",
               announce.purchase_agent as "purchaseAgent",
               announce.purchase_category as "purchaseCategory",
               announce.title as "title",
               announce.url as "url",
               announce.content_source as "contentSource",
               announce.website as "website",
               announce.province as "province",
               announce.city as "city",
               announce.county as "county",
               to_char(announce.published_ts, 'yyyy-mm-dd HH:MM:SS') as "publishedDateTime",
               to_char(announce.announced_ts, 'yyyy-mm-dd') as "announcedDate",
               to_char(announce.winning_ts, 'yyyy-mm-dd') as "winningDate",
               announce.announce_type as "announceType",
               announce.amount as "totalAmount",
               announce.unit as "totalAmountUnit",
               announce.currency as "totalAmountCurrency"
        from bidding_result result, bidding_announce announce
        where result.bidding_announce_id = announce.id
        and announce.url=%s;
"""

# 公司中标信息公告网页源码查询
company_bidding_content_source_query = """
        select
               announce.content_source as "contentSource"
        from bidding_announce announce
        where announce.id=%s;
"""

# ************************************** #
# 对公司的投标中标情况进行统计分析
# ************************************** #

bidding_result_statistic_by_company_query = """
        with temp as  (
            select BA.id, BR.winning_amount,  BR.role_type, BA.province
            from bidding_announce BA join bidding_result BR  on(BA.id=BR.bidding_announce_id)
            where BR.winning_company=%(company_name)s
            and BA.status<2
            and BA.published_ts>=%(start_date)s
            and BA.published_ts<=%(end_date)s
        ),
        bid_reg as (
            select
                case when province is null then '未知' else province end as "province",
                count(distinct(id)),
                sum(winning_amount)
            from temp
            group by province
        ),
        win_reg as (
            select
                case when province is null then '未知' else province end as "province",
                count(distinct(id)),
                sum(winning_amount)
            from temp
            where role_type='winner'
            group by province
        )
        select
            case when bid_reg.province='未知' then null else bid_reg.province end as "province",
            case when bid_reg.count is null then 0 else bid_reg.count end as "bidCount",
            bid_reg.sum as "bidMoneyAmount",
            case when win_reg.count is null then 0 else win_reg.count end as "winCount",
            win_reg.sum as "winMoneyAmount"
        from bid_reg left join  win_reg
        on bid_reg.province=win_reg.province;
"""

bidding_result_statistic_by_company_trend_query = """
        with temp as  (
            select BA.id, BR.winning_amount,  BR.role_type, BA.province, to_char(BA.published_ts, 'YYYYMM') as "year_month"
            from bidding_announce BA join bidding_result BR  on(BA.id=BR.bidding_announce_id)
            where BR.winning_company=%(company_name)s
            and BA.status<2
        ),
        bid_reg as (
            select
                year_month,
                case when province is null then '未知' else province end as "province",
                count(distinct(id)),
                sum(winning_amount)
            from temp
            group by province, year_month
        ),
        win_reg as (
            select
                year_month,
                case when province is null then '未知' else province end as "province",
                count(distinct(id)),
                sum(winning_amount)
            from temp
            where role_type='winner'
            group by province, year_month
        )
        select
            case when bid_reg.province='未知' then null else bid_reg.province end as "province",
            bid_reg.year_month as "yearMonth",
            case when bid_reg.count is null then 0 else bid_reg.count end as "bidCount",
            bid_reg.sum as "bidMoneyAmount",
            case when win_reg.count is null then 0 else win_reg.count end as "winCount",
            win_reg.sum as "winMoneyAmount"
        from bid_reg left join  win_reg
        on (bid_reg.year_month=win_reg.year_month and bid_reg.province=win_reg.province);
"""
