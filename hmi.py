#!/usr/bin/env python3


def create_app(app):
    """
    Sets up flask app to work with sqlalchemy database
    Creates users in database for login
    """
    import os

    app_root = os.path.dirname(
        __file__
    )  # Assuming this code is in your main application file

    # Specify the path to the database file in the /frontend/instance directory
    db_file_path = os.path.join(app_root, "HMI", "frontend", "instance", "login.db")
    from HMI.frontend.helpers.user_handler import db

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file_path}"
    from HMI.frontend.helpers.user_handler import generate_random_cookie

    app.secret_key = generate_random_cookie()
    db.init_app(app)
    from HMI.frontend.helpers.user_handler import create_users

    with app.app_context():  # create user database
        db.create_all()
        create_users()


def main():
    print('on main nnnnnnnnnnnnnnnnnnn')
    # Empty old logs
    for i in "12345":
        print('i : ' ,i)
        filename = "HMI/frontend/datalogger/logs/bs_log_" + i + ".txt"
        open(filename, "w", encoding="utf-8").close()
    filename = "HMI/frontend/datalogger/logs/system_log.txt"
    open(filename, "w", encoding="utf-8").close()
    import json
    print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
    # Fetch configuration from "config_HMI.json"
    with open("HMI/config_HMI.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    from HMI import modbus_master
    from HMI.frontend.gui import dashboard

    modbus_master.start_client()
    print("run dashboard jjjjjjjjjjjjjjjjjjj")
    print('json_data["HMI_WEBSERVICE"]["IP"] : ',json_data["HMI_WEBSERVICE"]["IP"])
    print('json_data["HMI_WEBSERVICE"]["PORT"] : ',json_data["HMI_WEBSERVICE"]["PORT"])
    dashboard.app.run(
        host=json_data["HMI_WEBSERVICE"]["IP"], port=json_data["HMI_WEBSERVICE"]["PORT"]
    )


if __name__ == "__main__":
    main()
