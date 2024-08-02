# tasks.py
from celery import shared_task
from .models import Loan

@shared_task(bind=True)
def save_data_task(self, data):
    task = Task.objects.get(task_id=self.request.id)
    try:
        Loan.objects.create(
            og_file=data.get('og_file'),
            developer=data.get('developer'),
            constructor=data.get('constructor'),
            trustee=data.get('trustee'),
            loan_amount=data.get('loan_amount'),
            loan_period=data.get('loan_period'),
            fee=data.get('fee'),
            irr=data.get('irr'),
            prepayment_fee=data.get('prepayment_fee'),
            overdue_interest_rate=data.get('overdue_interest_rate'),
            principal_repayment_type=data.get('principal_repayment_type'),
            interest_payment_period=data.get('interest_payment_period'),
            deferred_payment=data.get('deferred_payment'),
            joint_guarantee_amount=data.get('joint_guarantee_amount'),
            lead_arranger=data.get('lead_arranger'),
            company=data.get('company'),
        )
        task.status = states.SUCCESS
        task.result = {'status': 'success'}
    except Exception as e:
        task.status = states.FAILURE
        task.result = {'status': 'error', 'message': str(e)}
        self.update_state(state=states.FAILURE, meta={'exc': str(e)})
        raise Ignore()
    finally:
        task.save()
    return task.result