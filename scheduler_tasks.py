from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

def scheduled_story_generation():
    """Scheduled task to generate new AI stories"""
    from app import app, db, Story, Evidence
    from ai_engine import generate_ai_story_with_meta, should_generate_new_story, generate_evidence_image
    from story_engine import initialize_story_state
    import random
    
    with app.app_context():
        print(f"[{datetime.now()}] Running scheduled story generation...")
        
        if should_generate_new_story():
            story_data = generate_ai_story_with_meta()
            
            if story_data:
                story = Story(
                    title=story_data['title'],
                    content=story_data['content'],
                    category=story_data['category'],
                    location=story_data['location'],
                    is_ai_generated=True,
                    ai_persona=story_data['ai_persona']
                )
                
                db.session.add(story)
                db.session.flush()
                
                initialize_story_state(story)
                
                # 自动生成证据图片
                try:
                    evidence_paths = generate_evidence_image(
                        story_data['title'], 
                        story_data['content'],
                        story_data.get('category', 'urban_legend')
                    )
                    
                    evidence_descriptions = [
                        '【现场拍摄】刚才偷偷拍的，手有点抖。大家看出什么问题了吗？（手机拍摄，画质一般）',
                        '【证据照片】放大后能看到一些细节...我不知道该怎么解释这个。（iPhone夜间模式）',
                        '【更新】找到了之前拍的照片，上传给大家看看。注意看背景那里。（旧照片翻拍）',
                        '【局部特写】用手机放大拍的，不是很清楚但能看出个大概。（手机变焦拍摄）',
                        '【诡异】这张是什么情况？我发誓拍的时候没看到这个...（低光模式，有噪点）'
                    ]
                    
                    for idx, evidence_path in enumerate(evidence_paths):
                        from datetime import timedelta
                        evidence = Evidence(
                            story_id=story.id,
                            evidence_type='image',
                            file_path=evidence_path,
                            description=evidence_descriptions[idx % len(evidence_descriptions)],
                            created_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 120))
                        )
                        db.session.add(evidence)
                    
                    print(f"✅ 为故事创建了 {len(evidence_paths)} 个证据项")
                except Exception as e:
                    print(f"⚠️ 生成证据图片失败: {e}")
                
                db.session.commit()
                
                print(f"✅ Generated new story: {story.title}")
            else:
                print("❌ Failed to generate story")
        else:
            print("⏭️  Skipped: Max active stories reached")

def scheduled_state_progression():
    """Check and progress story states"""
    from app import app, db, Story
    from story_engine import check_state_transition, transition_story_state
    
    with app.app_context():
        print(f"[{datetime.now()}] Checking story state transitions...")
        
        active_stories = Story.query.filter(Story.current_state != 'ended').all()
        
        for story in active_stories:
            if check_state_transition(story):
                print(f"🔄 Transitioning story: {story.title}")
                transition_story_state(story, app.app_context)
                db.session.commit()
                print(f"✅ Story transitioned to: {story.current_state}")

def start_scheduler(app):
    """Initialize and start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Generate new stories every 5 minutes
    story_interval_minutes = int(os.getenv('STORY_GEN_INTERVAL_MINUTES', 5))
    scheduler.add_job(
        func=scheduled_story_generation,
        trigger='interval',
        minutes=story_interval_minutes,
        id='story_generation',
        name='Generate new AI urban legends',
        replace_existing=True
    )
    
    # Check story state progression every 30 minutes
    scheduler.add_job(
        func=scheduled_state_progression,
        trigger='interval',
        minutes=30,
        id='state_progression',
        name='Progress story states',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Background scheduler started!")
    print(f"   - Story generation: every {story_interval_minutes} minutes")
    print(f"   - State progression: every 30 minutes")
    
    return scheduler
