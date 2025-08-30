import sqlite3

conn = sqlite3.connect('emaildb.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Emails')
cur.execute('CREATE TABLE Emails (sender TEXT, subject TEXT, body TEXT)')

fname = input('Enter file name: ')
if len(fname) < 1:
    fname = 'mbox.txt'

fh = open(fname)

sender = None
subject = None
body_lines = []
reading_body = False

for line in fh:
    line = line.rstrip('\n')

    # Detect start of new email
    if line.startswith('From '):  # Real start of a new email in mbox format
        if sender and body_lines:
            body = '\n'.join(body_lines).strip()
            cur.execute('INSERT INTO Emails (sender, subject, body) VALUES (?, ?, ?)',
                        (sender, subject, body))
        sender = None
        subject = None
        body_lines = []
        reading_body = False
        continue

    if not reading_body:
        if line.startswith('From: '):
            sender = line[6:].strip()
        elif line.startswith('Subject: '):
            subject = line[9:].strip()
        elif line == '':
            # Blank line marks the start of the body
            reading_body = True
    else:
        body_lines.append(line)

# Insert last email if file ends without final 'From '
if sender and body_lines:
    body = '\n'.join(body_lines).strip()
    cur.execute('INSERT INTO Emails (sender, subject, body) VALUES (?, ?, ?)',
                (sender, subject, body))

conn.commit()

# Sample query to show result
print("\nSample emails:")
for row in cur.execute('SELECT sender, subject, substr(body, 1, 100) || "..." FROM Emails LIMIT 5'):
    print(f"\nSender: {row[0]}\nSubject: {row[1]}\nBody Preview: {row[2]}")

cur.close()
