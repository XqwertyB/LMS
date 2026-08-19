from content.models import Content, Content_teacher, Topic, Video_content, File_content, Content_teacher, Task, \
    Task_students, Task_file


def countremain(task):
    try:
        score = task.topic_id_task.content_teacher_connect.totatl_score_jn
        topics = task.topic_id_task.content_id_topic.content_set_topic.all()
        summa = 0
        for item in topics:
            if item.topic_set_task:
                for var in item.topic_set_task.all():
                    summa += var.score
        content = {
            'error': True,
            'results': {
                'score_jn': score,
                'scorereamin': score - summa}
        }
        return content
    except Exception as ex:
        content = {
            'error': False,
            'message': str(ex)
        }
        return content


def countremaintopic(topic):
    try:
        score = topic.content_teacher_connect.totatl_score_jn
        topics = topic.content_teacher_connect.content_id.content_set_topic.all()
        content_teacher_connect = topic.content_teacher_connect
        summa = 0
        for item in topics:
            if item.content_teacher_connect == content_teacher_connect:
                if item.topic_set_task:
                    for var in item.topic_set_task.all():
                        summa += var.score
        content = {
            'error': True,
            'results': {
                'score_jn': score,
                'scorereamin': score - summa}
        }
        return content
    except Exception as ex:
        content = {
            'error': False,
            'message': str(ex)
        }
        return content
