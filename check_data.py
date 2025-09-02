from projects.models import ProjectStatusLog
from tickets.models import TicketStatusLog

print(f'Total ProjectStatusLog entries: {ProjectStatusLog.objects.count()}')
print('Sample project status log entries:')
for log in ProjectStatusLog.objects.all()[:5]:
    print(f'  - Project {log.project.id}: {log.status} at {log.timestamp}')

print(f'\nTotal TicketStatusLog entries: {TicketStatusLog.objects.count()}')
print('Sample ticket status log entries:')
for log in TicketStatusLog.objects.all()[:5]:
    print(f'  - Ticket {log.ticket.id}: {log.status} at {log.timestamp}')