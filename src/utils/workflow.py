from crontab import CronTab


def reschedule_cron_job(sys_user, job_comment, schedule, logger_instance):
    """
    Summary:
        Function sets schedule for an exisitng cronjob.
    Args:
        sys_user (variable): os session user name,
        job_comment (str): comment attached to cronjob details as tag name.
        schedule (str): Standard cronjob scheduling string eg: '0 10 * * *'.
    """   
    try:
        cron = CronTab(sys_user)
        for job in cron:
            if job.comment == job_comment:
                job.setall(schedule)
                cron.write()
                logger_instance.info(f"The '{job.comment}' cron job has been successfully reset as follows:\n{job}")
    except Exception as e:
        logger_instance.error(f"Unable to reset cron job to {schedule}. {str(e)}")