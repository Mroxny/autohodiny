# autohodiny

A Python script that automatically fills timesheet entries on a hodiny web portal based on a predefined schedule. Features Discord notifications and end-of-month reminders.


## Prerequisites

- Python 3.6+
- Google Chrome browser installed
- ChromeDriver (see Installation section)

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Mroxny/autohodiny.git
   cd autohodiny
   ```

2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```


## Usage

Fill the `values.yaml` file according to your needs and run the script:

```bash
python app.py
```

### Scheduled Automation
For daily execution, set up a scheduler:

* **Linux/Mac**: Use cron
    ```bash
    0 18 * * 1-5 cd /path/to/script && python app.py
    ```
* **Windows**: Use Task Scheduler

