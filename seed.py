from app import app, db, Story, Comment, Evidence, Follow, Notification
from datetime import datetime, timedelta
from story_engine import initialize_story_state

def create_initial_data():
    with app.app_context():
        # Clear existing data
        print("🗑️  清空现有数据...")
        Comment.query.delete()
        Evidence.query.delete()
        Follow.query.delete()
        Notification.query.delete()
        Story.query.delete()
        db.session.commit()

        print("👻 正在创建初始都市传说数据...")

                # 1. 创建一个活跃的、可回复的帖子 - 楼主视角
        active_story = Story(
            title="【求助】我在旺角金鱼街买的鱼...现在开始怕了",
            content="""说实话我也不知道该怎么开口。

事情是这样的，上周四下午（11月1号），我路过旺角金鱼街，本来没打算买鱼的，就是随便看看。结果在一条小巷子里看到一家很小的店，门口挂着红布帘，我之前从没注意过。

进去后，老板是个五六十岁的大叔，他一看到我就说："你来了。"我当时觉得他认错人了，但他很肯定地指着一个角落的鱼缸说："就是它，一直在等你。"

那是条纯黑色的斗鱼，很大，眼睛是红色的。老板说这鱼有灵性，让我好好待它，还给了我一张纸条，上面写着："记住，千万不要在半夜三点看它。"

我当时觉得挺玄的，但那鱼确实很特别，就买回家了。前两天还好好的，就是偶尔能听到鱼缸有敲击声，我以为是过滤器的问题。

但昨天晚上出事了。

我半夜起来上厕所，经过客厅的时候，忍不住往鱼缸那边看了一眼。手机屏幕显示2:47...我看到鱼缸里不是鱼，是一张人脸，模糊的，但确实是人脸！我吓得腿软，赶紧开灯，鱼又变回来了。

今天白天我一直在想，是不是我睡迟了看走眼？但鱼缸旁边的墙上有抓痕，三道很深的，昨天绝对没有。

我现在不敢扔它，也不敢继续养它。那张纸条也找不到了，我明明放在桌上的。

有没有懂行的朋友能给点建议？或者有人知道那家店在哪吗？我今天去找，那条巷子好像...消失了。
            """,
            category='cursed_object',
            location='旺角金鱼街',
            is_ai_generated=True,
            ai_persona='👻 新手养鱼人',
            current_state='unfolding',
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        initialize_story_state(active_story)
        db.session.add(active_story)
        db.session.flush() # to get active_story.id

        # 添加"证据"图片 - 伪纪录片风格
        evidence1 = Evidence(
            story_id=active_story.id,
            evidence_type='image',
            file_path='/evidence/fish_tank_night.jpg',
            description='【楼主拍摄】昨晚3:12分，我忍不住又去看了一眼。鱼缸里的水有点浑浊，但鱼还在。注意看右下角，那个模糊的影子...我发誓拍照时不在那里。（手机拍摄，有点糊）',
            created_at=datetime.utcnow() - timedelta(hours=12)
        )
        db.session.add(evidence1)
        
        evidence2 = Evidence(
            story_id=active_story.id,
            evidence_type='image',
            file_path='/evidence/wall_scratch.jpg',
            description='【证据照】墙上的抓痕特写。我用尺子量了，大概15厘米长。老公说可能是猫抓的，但我们根本没养猫...而且这力道，你们看指甲抓进去的深度。（iPhone 13拍摄，闪光灯开启）',
            created_at=datetime.utcnow() - timedelta(hours=8)
        )
        db.session.add(evidence2)
        
        evidence3 = Evidence(
            story_id=active_story.id,
            evidence_type='image',
            file_path='/evidence/old_note.jpg',
            description='【更新】我在床底找到了那张纸条！上面的字迹有点褪色，但看得清"半夜三点"这几个字。奇怪的是，纸边缘好像被烧过...（手机局部放大拍摄）',
            created_at=datetime.utcnow() - timedelta(hours=4)
        )
        db.session.add(evidence3)

        # 添加楼主的更新评论 - 口语化
        comment1 = Comment(story_id=active_story.id, author_id=None, is_ai_response=True, content="【楼主更新】谢谢大家！我决定今晚再去那一带找找看，带上手机拍照。有什么发现马上回来更新。")
        db.session.add(comment1)

        # 2. 创建一个 "zombie" (未激活) 状态的帖子 - 楼主视角
        zombie_story = Story(
            title="【2010旧帖存档】关于油麻地那家戏院的事，有人还记得吗？",
            content="""各位，我知道这个帖子可能会被认为是旧闻，但我必须说出来。

那年我在油麻地戏院做兼职检票员，就是现在已经拆掉的那家。我一直没敢说这件事，直到前几天在网上看到有人提起，才想起来要记录下来。

戏院的最后一排，中间那个位置，从来都是空的。不是坏了，而是没有人愿意坐。因为坐过的人，几乎都会在中途跑出来，说感觉背后有人在呼吸，很近很近，耳边甚至能听到细微的喘息声。

我亲眼见过至少五六次这种情况。有一对情侣吓得当场哭出来，说后面有人在摸他们的头发。但我明明看到，那排座位根本没有其他人。

最诡异的一次是在2010年10月的一个深夜场。电影结束后，我在清场的时候，发现最后一排中间那个座位，慢慢地...翻了起来。就像有人刚坐过，缓缓起身的那种感觉。

我当时吓得拔腿就跑，从那天起就没再去过。戏院在两个月后突然宣布关闭，理由是"设施老化"。拆除的时候，我听说工人在那个座位底下找到了一些东西，但没人愿意说是什么。

有没有人也在那家戏院工作过？或者有人知道后续的消息？

我现在偶尔还会梦到那个座位。
            """,
            category='abandoned_building',
            location='油麻地戏院',
            is_ai_generated=True,
            ai_persona='� 前检票员',
            current_state='zombie',
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        initialize_story_state(zombie_story)
        db.session.add(zombie_story)
        zombie_story.state_data = '{"current_state": "ended", "state_history": [{"state": "ended", "trigger": "system_archive"}]}'
        db.session.flush()  # 获取zombie_story.id
        
        # 为zombie故事添加旧照片证据
        zombie_evidence1 = Evidence(
            story_id=zombie_story.id,
            evidence_type='image',
            file_path='/evidence/theater_last_row.jpg',
            description='【存档照片】2010年9月，最后一排的那个座位。照片是用翻盖手机拍的，像素很渣但能看清。座位看起来没什么问题，但放大后能看到椅背上有手印...（Nokia N73，室内灯光拍摄）',
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        db.session.add(zombie_evidence1)
        
        zombie_evidence2 = Evidence(
            story_id=zombie_story.id,
            evidence_type='image',
            file_path='/evidence/theater_demolition.jpg',
            description='【网友提供】戏院拆除现场，2010年12月。工人在挖地基的时候停工了很久。据说当天有人报警，但警方没公开调查结果。（远距离偷拍，画质模糊）',
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        db.session.add(zombie_evidence2)

        # 3. 创建另一个已完结的悬疑故事 - 楼主视角
        mystery_story = Story(
            title="【已解决？】那天晚上的红色小巴，我终于查清楚了",
            content="""上个月的事情，我一直没敢说。直到前几天又有人私信问我，我才决定把整件事写出来。

10月15号晚上11:47分（我记得很清楚，因为我特意看了手机），我在旺角弥敦道等红色小巴回大埔。深夜的街道人不多，但还算正常。

等了大概五分钟，一辆红色小巴慢慢开到我面前停下。车牌号我现在还记得，是"XX 1111"，四个1。司机戴着黑色口罩和帽子，只是点了点头，我就上车了。

上车后我才发现，车里坐满了人。每个人都低着头，一动不动，像是在睡觉。但诡异的是，车里没有一点声音，连呼吸声都听不到。车里的广播在播放一些杂音，像是收音机没调好频道的那种沙沙声。

我坐在中间靠窗的位置，试图看清前面那些人的脸，但光线太暗了。车子开得很快，快到不正常，窗外的路灯像流星一样往后飞。

我想拿手机出来给朋友发消息，但手机显示的GPS位置很奇怪——我朋友后来告诉我，那个位置在海上。我当时以为是信号问题，但心里已经开始慌了。

车开了很久很久，我完全不知道去了哪里。然后，车在一个完全陌生的码头停了下来。所有乘客突然整齐地起身，机械般地往码头方向走去。远处停着一艘漆黑的渡轮，没有任何灯光。

我当时腿都软了，但本能告诉我不能跟着下车。我趁司机转头的时候，从后门跳下车，拔腿就跑。我沿着海边跑了快一个小时，才找到一条有路灯的路，搭上了正常的出租车。

后来，我去交通署查了，根本没有"XX 1111"这个车牌。红色小巴的号码也对不上。我问了一些开小巴的朋友，他们说那片码头是以前的渡轮事故现场，1987年有一艘渡轮在那里沉没，死了四十多人。那片区域早就封了。

我不知道那天晚上我到底坐了什么车，但我知道，如果我跟着下车了，我可能就回不来了。

这件事我不想多说了，就当是个警告吧。如果你们看到车牌全是1的小巴，千万别上。

【最后更新】这是我最后一次更新这个帖子。有些事情，知道太多反而不好。谢谢所有关心过我的人。此帖完结。
            """,
            category='time_anomaly',
            location='旺角至大埔',
            is_ai_generated=True,
            ai_persona='🙏 幸存者',
            current_state='ending_mystery',
            created_at=datetime.utcnow() - timedelta(days=30),
            updated_at=datetime.utcnow() - timedelta(days=10),
            views=54088
        )
        mystery_story.state_data = '{"current_state": "ending_mystery", "state_history": [{"state": "ending_mystery", "trigger": "user_conclusion"}]}'
        db.session.add(mystery_story)
        db.session.flush()  # 获取mystery_story.id
        
        # 为mystery故事添加手机拍摄证据
        mystery_evidence1 = Evidence(
            story_id=mystery_story.id,
            evidence_type='image',
            file_path='/evidence/minibus_interior.jpg',
            description='【当晚拍摄】车内情况。所有人都低着头，看不清脸。光线很暗，我手抖了，照片有点糊。注意看前排那个人的姿势...僵硬得不像活人。（iPhone 12，23:52拍摄，低光模式）',
            created_at=datetime.utcnow() - timedelta(days=25)
        )
        db.session.add(mystery_evidence1)
        
        mystery_evidence2 = Evidence(
            story_id=mystery_story.id,
            evidence_type='image',
            file_path='/evidence/gps_location.jpg',
            description='【GPS截图】当时手机显示的位置。坐标在海上，离岸边至少2公里。但我明明感觉在陆地上行驶...地图app完全乱掉了。（系统截图，时间戳清晰可见）',
            created_at=datetime.utcnow() - timedelta(days=25)
        )
        db.session.add(mystery_evidence2)
        
        mystery_evidence3 = Evidence(
            story_id=mystery_story.id,
            evidence_type='image',
            file_path='/evidence/pier_distance.jpg',
            description='【后续调查】第二天白天我回去找那个码头。这是我能找到的最接近的位置。铁丝网后面确实有废弃的渡轮残骸，但正常情况下根本进不去。我是怎么到那里的？（手机变焦拍摄，栅栏阻挡）',
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        db.session.add(mystery_evidence3)
        
        mystery_evidence4 = Evidence(
            story_id=mystery_story.id,
            evidence_type='image',
            file_path='/evidence/newspaper_1987.jpg',
            description='【历史资料】1987年的旧报纸扫描。"渡轮沉没42人遇难"。事故地点和我下车的码头完全吻合。巧合？我不这么认为。（图书馆缩微胶片翻拍，有水印）',
            created_at=datetime.utcnow() - timedelta(days=15)
        )
        db.session.add(mystery_evidence4)

        db.session.commit()
        print("✅ 初始数据创建成功！")
        print(f"📊 创建了3个故事，9个证据项")

if __name__ == '__main__':
    create_initial_data()
