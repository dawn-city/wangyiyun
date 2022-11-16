
from pyecharts.charts import Map,Bar,Line,Pie,WordCloud,Grid
import pyecharts.options as opts
from pyecharts.components import Table
from . import mysql
import datetime
import os 
import jieba


base_dir=os.path.dirname(os.path.abspath(__file__))
# mask_image='data:image/png;base64,'+base64.b64encode(open(os.path.join(base_dir,'netease.png'),'rb').read()).decode()
mask_image=os.path.join(base_dir,'netease.png')
# print(mask_image)

def render_echarts(type='summary'):
    cur = mysql.connection.cursor()
    #数据概览
    if type=='summary':
        headers=['类目','数量']
        cur.execute('''
        select '歌单' as type,count(1) as num
        from playlists
        union all
        select '歌曲' as type,count(1) as num
        from tracks
        union all
        select '评论' as type,count(1) as num
        from hot_comments;
        ''')
        data = cur.fetchall()
        table_data=[]
        for d in data:
            table_data.append([d['type'],d['num']])
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="网易云音乐采集数量")
        )
        return table.render_embed()
    
    #歌曲歌单数量范围，返回饼图
    elif type=='playlist_songs_range':
        cur.execute('''
            SELECT songnum,count(1) as num
            from 
            (
            select *,case when track_count<=10 then '<=10' 
                when track_count<=20 then '10-20'
                when track_count<=50 then '20-50' 
                when track_count<=100 then '50-100' 
                when track_count<=200 then '100-200' 
                when track_count<=500 then '200-500' 
                when track_count<=1000 then '500-1000' 
                else '>1000' 
            end as songnum  
            from playlists
            ) t
            GROUP BY songnum
            order by FIELD(songnum,'<=10','10-20','20-50','50-100','100-200','200-500','500-1000','>1000')
        ''')
        data = cur.fetchall()
        x_data=[]
        y_data=[]
        for d in data:
            x_data.append(d['songnum'])
            y_data.append(d['num'])
        c=(
            Pie(init_opts=opts.InitOpts(width="1600px", height="1000px"))
            .add(
                series_name="kingbob",
                data_pair=[list(z) for z in zip(x_data, y_data)],
                center=["50%", "50%"],
                radius=["50%", "70%"],
                label_opts=opts.LabelOpts(is_show=False, position="center"),
            )
            .set_global_opts(legend_opts=opts.LegendOpts(pos_left="legft", orient="vertical"))
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(
                    trigger="", formatter="{a} <br/>{b}: {c} ({d}%)"
                ),
                label_opts=opts.LabelOpts(formatter="{b}:({d}%)")
            )
        )
        return c.dump_options_with_quotes()
    
    #不同语种歌单播放量
    elif type=='lan_play_count':
        cur.execute('''
        SELECT *
        from
        (
            select tag,sum(play_count) as play_count
            from (
            select a.*,substring_index(
                    substring_index(a.tags, ',',b.number), 
                    ',', 
                    -1
            ) as tag
            from playlists a
            join numbers b
            on char_length(a.tags) 
                    - char_length(replace(a.tags, ',', '')) 
                    >= b.number - 1
                            ) t
                        
            GROUP BY tag
            order by play_count desc
        ) g 
        where tag in ('华语','欧美','韩语','粤语','日语','小语种')
        ''')
        data = cur.fetchall()
        x_data=[]
        y_data=[]
        for d in data:
            x_data.append(d['tag'])
            y_data.append(d['play_count'])
        c = (
            Pie()
            .add(
                "",
                data_pair=[list(z) for z in zip(x_data, y_data)],
                radius=["30%", "75%"],
                center=["50%", "50%"],
                rosetype="radius",
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(
                    trigger="", formatter="{a} <br/>{b}: {c} ({d}%)"
                ),
                label_opts=opts.LabelOpts(formatter="{b}:({d}%)")
            )
            
        )
        return c.dump_options_with_quotes()

    #播放次数前10的歌单，返回table
    elif type=='top10List':
        cur.execute('''
        select `name`,play_count,share_count,track_count,tags
        from playlists
        order by play_count desc
        limit 10;
        ''')
        data = cur.fetchall()
        headers=['歌单','播放次数','分享次数','歌曲数','标签']
        table_data=[]
        for d in data:
            table_data.append([d['name'],d['play_count'],d['share_count'],d['track_count'],d['tags']])
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="网易云音乐播放次数前10的歌单")
        )
        return table.render_embed()

    #播放次数前10的歌单标签，返回标签饼图
    elif type=='top10List_pie':
        cur.execute('''
        select `name`,tags,play_count
        from playlists
        order by play_count desc
        limit 10;
        ''')
        data = cur.fetchall()
        tags={}
        for d in data:
            t=d['tags'].split(',')
            for tag in t:
                tags.setdefault(tag,0)
                tags[tag]+=1
        tags_list=[]
        for tag in tags:
            tags_list.append([tag,tags[tag]])
        tags_list.sort(key=lambda x:x[1],reverse=True)
        c=(
            Pie()
            .add("",
                tags_list,
                center=["50%","50%"],
                label_opts=opts.LabelOpts(formatter="{b}:({d}%)")
            )
        )
        return c.dump_options_with_quotes()

    #歌单根据类型分组，画饼图
    elif type=='tag':
        cur.execute('''              
        select tag,count(1) as num
        from (
        select a.*,substring_index(
            substring_index(a.tags, ',',b.number), 
            ',', 
            -1
        ) as tag
        from playlists a
        join numbers b
        on char_length(a.tags) 
            - char_length(replace(a.tags, ',', '')) 
            >= b.number - 1
                ) t
                GROUP BY tag
        order by num desc
        limit 10
        ''')
        data = cur.fetchall()
        tag_list=[]
        for d in data:
            tag_list.append((d['tag'],d['num']))
        c=Pie().add("",tag_list,center=["50%","50%"],label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        return c.dump_options_with_quotes()

    #标签词云，自定义图片
    elif type=='alltag_cloudword':
        cur.execute('''              
        select tag,count(1) as num
        from (
        select a.*,substring_index(
            substring_index(a.tags, ',',b.number), 
            ',', 
            -1
        ) as tag
        from playlists a
        join numbers b
        on char_length(a.tags) 
            - char_length(replace(a.tags, ',', '')) 
            >= b.number - 1
                ) t
                GROUP BY tag

        ''')
        data = cur.fetchall()
        tag_list=[]
        for d in data:
            tag_list.append((d['tag'],d['num']))
        c=WordCloud().add("", tag_list,  word_size_range=[20, 100],width=1000,height=600)\
            .set_global_opts(title_opts=opts.TitleOpts(title="网易云音乐标签词云"))
        return c.dump_options_with_quotes()
    
    #歌曲分类: 总数、原唱、翻唱
    elif type=='song_data':
        cur.execute('''
        select '总数' as type,count(1) as num
        from tracks

        union all 

        select '原唱' as type,count(1) as num
        from tracks
        where not ((publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0)
        union all 

        select '翻唱' as type,count(1) as num
        from tracks
        where (publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0
        ''')
        data = cur.fetchall()
        headers=['类型','数量']
        table_data=[]
        for d in data:
            table_data.append([d['type'],d['num']])
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="网易云音乐歌曲分类", subtitle="数据来源于网易云音乐")
        )
        return table.render_embed()
    
    #被引用最多的歌曲top10,返回柱状图
    elif type=='song_ref':
        cur.execute('''
        select track_ids
        from playlists
        ''')
        data = cur.fetchall()
        track_ids={}
        for d in data:
            for track_id in d['track_ids'].split(','):
                if track_id not in track_ids:
                    track_ids[track_id]=1
                else:
                    track_ids[track_id]+=1
        #取top10
        track_ids_list=sorted(track_ids.items(),key=lambda x:x[1],reverse=True)[:10]
        x=[]
        y=[]
        for track_id,ref_num in track_ids_list:
            cur.execute('''
            select name,publishTime,artists,comment_count
            from tracks
            where id=%s
            ''',(track_id,))
            data = cur.fetchone()
            publishTime=data['publishTime']
            publishTime=datetime.datetime.fromtimestamp(int(publishTime[:10])).strftime('%Y-%m-%d') if publishTime!='0' else '未知'
            x.append(data['name'])
            y.append(ref_num)

        x=x[::-1]
        y=y[::-1]
        c=Bar().add_xaxis(x).add_yaxis('',y,label_opts=opts.LabelOpts(is_show=False))\
            .set_global_opts(title_opts=opts.TitleOpts(title='被引用最多的歌曲TOP10',pos_right='center'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=60))
        ).reversal_axis()
        return c.dump_options_with_quotes()
    #被引用最多的歌曲top10,返回table
    elif type=='song_ref_table':
        cur.execute('''
        select track_ids
        from playlists
        ''')
        data = cur.fetchall()
        track_ids={}
        for d in data:
            for track_id in d['track_ids'].split(','):
                if track_id not in track_ids:
                    track_ids[track_id]=1
                else:
                    track_ids[track_id]+=1
        #取top10
        track_ids_list=sorted(track_ids.items(),key=lambda x:x[1],reverse=True)[:10]
        headers=['歌曲名','歌手','评论数','发布时间','被引用次数']
        table_data=[]
        for track_id,ref_num in track_ids_list:
            cur.execute('''
            select name,publishTime,artists,comment_count
            from tracks
            where id=%s
            ''',(track_id,))
            data = cur.fetchone()
            publishTime=data['publishTime']
            publishTime=datetime.datetime.fromtimestamp(int(publishTime[:10])).strftime('%Y-%m-%d') if publishTime!='0' else '未知'
            table_data.append([data['name'],data['artists'],data['comment_count'],publishTime,ref_num])

        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="被引用最多的歌曲TOP10", subtitle="数据来源于网易云音乐")
        )
        return table.render_embed()

    #热门歌曲top10（根据评论次数）,返回柱状图
    elif type=='hot_song':
        cur.execute('''
        select name,comment_count
        from tracks
        order by comment_count desc
        limit 10
        ''')
        data = cur.fetchall()
        x=[]
        y=[]
        for d in data:
            x.append(d['name'])
            y.append(d['comment_count'])
        x=x[::-1]
        y=y[::-1]
        c=Bar().add_xaxis(x).add_yaxis('',y,label_opts=opts.LabelOpts(is_show=False))\
            .set_global_opts(title_opts=opts.TitleOpts(title='评论最多的歌曲TOP10',pos_right='center'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=60))
        ).reversal_axis()
        return c.dump_options_with_quotes()
    
    #热门歌曲top10（根据评论次数），返回table
    elif type=='hot_song_table':
        cur.execute('''
        select name,publishTime,artists,comment_count
        from tracks
        order by comment_count desc
        limit 10
        ''')
        data = cur.fetchall()
        headers=['歌曲名','歌手','评论数','发布时间']
        table_data=[]
        for d in data:
            publishTime=d['publishTime']
            publishTime=datetime.datetime.fromtimestamp(int(publishTime[:10])).strftime('%Y-%m-%d') if publishTime!='0' else '未知'
            table_data.append([d['name'],d['artists'],d['comment_count'],publishTime])
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="评论最多的歌曲TOP10", subtitle="数据来源于网易云音乐")
        )
        return table.render_embed()

    #被翻唱最多的歌曲top10，返回table
    elif type=='fan_song_table':
        cur.execute('''
        SELECT t1.*,t2.artists
        from 
        (
            SELECT new_name,count(1) as num
            from 
            (
                SELECT *,substring_index(substring_index(substring_index(name,'(',1),'（',1),'-',1) as new_name
                from tracks
                where ((publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0)
            ) t
            WHERE new_name!=''
            group by new_name
            order by num desc 
            limit 10
        ) t1
        left outer join 
        (
            SELECT a.* from tracks a right outer join (
                SELECT `name`,min(cast(id as UNSIGNED)) id
                from tracks 
                GROUP BY  `name`
            ) b	on a.id=b.id
        ) t2 
        on t1.new_name=t2.`name`
        order by num desc
        ''')
        data = cur.fetchall()
        headers=['歌曲名','原唱歌手','被翻唱次数']
        table_data=[]
        for d in data:
            table_data.append([d['new_name'],d['artists'],d['num']])
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="被翻唱最多的歌曲TOP10", subtitle="数据来源于网易云音乐")
        )
        return table.render_embed()
    
    #被翻唱歌曲，返回词云
    elif type=='fan_song_wordcloud':
        cur.execute('''
	SELECT new_name,count(1) as num
	from 
	(
		SELECT *,substring_index(substring_index(substring_index(name,'(',1),'（',1),'-',1) as new_name
		from tracks
		where ((publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0)
	) t
	WHERE new_name!=''
	group by new_name
	order by num desc 
        ''')
        data = cur.fetchall()
        song_list=[]
        for d in data:
            song_list.append((d['new_name'],d['num']))
        c=WordCloud().add("", song_list, word_size_range=[20, 100],width=1000,height=600)
        return c.dump_options_with_quotes()
    
    #歌曲最多的歌手top10，返回table
    elif type=='artist_most_table':
        cur.execute('''
        select artist,count(1) as num
        ,sum(if(is_original2='原唱',1,0)) as yc
        ,sum(if(is_original2='翻唱',1,0)) as fc
        from 
        (
            select a.*,if(not ((publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0),'原唱','翻唱') as is_original2
            ,substring_index(substring_index(a.artists, ',',b.number), ',', -1) as artist
            from tracks a
            join numbers b
                on char_length(a.artists) - char_length(replace(a.artists, ',', '')) >= b.number - 1
            
        ) t
        where artist not in ('','陈致逸','陈阳','V.A.','Audiomachine','Various Artists','')
        GROUP BY artist
        HAVING count(1)<200
        order by num desc 
        limit 10
        ''')
        data = cur.fetchall()
        headers=['歌手','歌曲数','原唱歌曲','翻唱歌曲']
        table_data=[]
        for d in data:
            table_data.append([d['artist'],d['num'],d['yc'],d['fc']])
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="歌曲最多的歌手TOP10", subtitle="数据来源于网易云音乐")
        )
        return table.render_embed()
    
    #歌曲最多的歌手，返回stack bar
    elif type=='artist_most':
        cur.execute('''
        select artist,count(1) as num
        ,sum(if(is_original2='原唱',1,0)) as yc
        ,sum(if(is_original2='翻唱',1,0)) as fc
        from 
        (
            select a.*,if(not ((publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0),'原唱','翻唱') as is_original2
            ,substring_index(substring_index(a.artists, ',',b.number), ',', -1) as artist
            from tracks a
            join numbers b
                on char_length(a.artists) - char_length(replace(a.artists, ',', '')) >= b.number - 1
            
        ) t
        where artist not in ('','陈致逸','陈阳','V.A.','Audiomachine','Various Artists','')
        GROUP BY artist
        HAVING count(1)<200
        order by num desc 
        limit 10
        ''')
        data = cur.fetchall()
        x=[]
        y1=[]
        y2=[]
        for d in data:
            x.append(d['artist'])
            y1.append(d['yc'])
            y2.append(d['fc'])
        c=Bar()\
            .add_xaxis(x)\
            .add_yaxis("原唱",y1,stack='stack1')\
            .add_yaxis("翻唱",y2,stack='stack1')\
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))\
            .set_global_opts(title_opts=opts.TitleOpts(title="歌曲最多的歌手TOP10", subtitle="数据来源于网易云音乐"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30)),
            )
        return c.dump_options_with_quotes()
    
    #歌曲被翻唱最多的歌手top10，返回table
    elif type=='artist_fan_song_table':
        cur.execute('''
	SELECT new_name,count(1) as num
	from 
	(
		SELECT *,substring_index(substring_index(substring_index(name,'(',1),'（',1),'-',1) as new_name
		from tracks
		where ((publishTime=0 and (name like '%(%' or name like '%（%')) or is_original=0)
	) t
	WHERE new_name!=''
	group by new_name
	order by num desc 
        ''')
        data = cur.fetchall()
        #查询原唱歌手
        artists_dict={}
        for d in data:
            cur.execute('''
            select artists
            from tracks
            where name=%s
            order by cast(id as UNSIGNED) asc limit 1
            ''',(d['new_name'],))
            artists=cur.fetchone()['artists']
            artists_dict.setdefault(artists,0)
            artists_dict[artists]+=1
        headers=['歌手','歌曲被翻唱次数']
        table_data=[]
        for d in data:
            table_data.append([d['new_name'],artists_dict[d['new_name']]])
        table_data=sorted(table_data,key=lambda x:x[1],reverse=True)[:10]
        table=Table().add(headers,table_data).set_global_opts(
            title_opts=opts.TitleOpts(title="歌曲被翻唱最多的歌手TOP10", subtitle="数据来源于网易云音乐")
        )
        return table.render_embed()



def jieba_cut(content_list,wordlists):
    #分词
    all_words=[]
    for content in content_list:
        seg_list = jieba.cut(content)
        seg_list = [i for i in seg_list if i != ' ']
        all_words.extend(seg_list)

    # 词频统计
    c = {}
    for x in all_words:
        if len(x)>1 and x != '\r\n':
            c.setdefault(x, 0)
            c[x] += 1

    words = []
    for (k,v) in c.items():
        # print(k, v)
        if k in wordlists:
            words.append((k,v))
    return words

family_words=['爸爸','妈妈','男朋友','女朋友','爷爷','奶奶','哥哥','姐姐','老公','老婆']
emotion_words=['开心','快乐','大笑','难过','痛苦','心酸','欢喜','哭','流泪']
gq_words=['单身','恋爱','离婚','分手','结婚']

def render_emotion(type,tag):
    cur = mysql.connection.cursor()
    #根据标签查询歌曲的热门评论
    if type=='family':
        type_cn='亲属'
        word_lists=family_words
    elif type=='emotion':
        type_cn='心情'
        word_lists=emotion_words
    elif type=='gq':
        type_cn='情感'
        word_lists=gq_words
    
    cur.execute('''
    SELECT track_ids
    from playlists
    where tags like '%%%s%%'
    order by play_count desc
    limit 10
    '''%tag)
    data = cur.fetchall()
    track_ids=[]
    for d in data:
        track_ids.extend(d['track_ids'].split(','))
    track_ids=list(set(track_ids))
    track_ids=','.join(track_ids)
    # print(track_ids)
    #根据歌曲id查询评论
    cur.execute('''
    SELECT content
    from hot_comments
    where track_id in (%s)
    '''%track_ids)
    data = cur.fetchall()
    content_lists=[]
    for d in data:
        content_lists.append(d['content'])
    most_word=jieba_cut(content_lists,word_lists)
    #绘制柱状图
    c=(
        Bar()
        .add_xaxis(list(map(lambda x:x[0],most_word)))
        .add_yaxis("",list(map(lambda x:x[1],most_word)))
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{tag}歌曲热评词频统计 - {type_cn} "),
                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30)),
                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}次"))
        )
    )
    return c.dump_options_with_quotes()
