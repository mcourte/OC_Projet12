import click
from cli import contract_cli, customer_cli, epic_cli, event_cli, user_cli


@click.group(help="------ CRM EpicEvent ------")
def main():
    pass


main.add_command(epic_cli.login)
main.add_command(epic_cli.logout)
main.add_command(epic_cli.dashboard)
main.add_command(epic_cli.initbase)
main.add_command(user_cli)
main.add_command(customer_cli)
main.add_command(contract_cli)
main.add_command(event_cli)


if __name__ == '__main__':
    main()
