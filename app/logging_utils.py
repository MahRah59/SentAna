from logging.handlers import SMTPHandler
import logging
import traceback

class CustomEmailHandler(SMTPHandler):
    def emit(self, record):
        try:
            record.message = self.format(record)
            subject = self.getSubject(record)

            # Custom email body
            body = f"""
🚨 SentAna Admin Alert

Level: {record.levelname}
Time: {self.formatTime(record)}
User: {getattr(record, 'user_email', '-')} (ID: {getattr(record, 'user_id', '-')})
Logger: {record.name}
Function: {record.funcName} (Line {record.lineno})

Message:
{record.getMessage()}

Traceback:
{traceback.format_exc()}
"""

            # Send email
            self.mailhost = (self.mailhost, self.mailport)
            smtp = self._connect()
            msg = f"From: {self.fromaddr}\r\nTo: {','.join(self.toaddrs)}\r\nSubject: {subject}\r\n\r\n{body}"
            smtp.sendmail(self.fromaddr, self.toaddrs, msg.encode("utf-8"))
            smtp.quit()

        except Exception:
            self.handleError(record)
