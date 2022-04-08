from datetime import datetime

from controller.credentals_controller import CredentialsController
from controller.event_controller import EventController
from dao.event_repository import EventRepository
from dao.group_repository import GroupRepository
from dao.id_generator_uuid import IdGeneratorUuid
from dao.user_repository import UserRepository
from entity.event_meeting import EventMeeting, EventStatusName, EventPost, EventInvitation, InvitationResponseTypeName
from entity.group import Group
from entity.user import RoleName, User
from service.event_service import EventService
from service.group_service import GroupService
from service.credentials_service import CredentialsService
from service.user_service import UserService
from view.components.main_credentials_view import MainCredentialsView
from tkinter import *

from view.utils.tkinter_utils import center_resize_window


def print_repo_entity(repo):
    for p in repo:
        print(p.get_formatted_str())


if __name__ == '__main__':

    user_repository = UserRepository(IdGeneratorUuid(), 'output_json_db/users_db.json')
    user_service = UserService(user_repository)
    event_repo = EventRepository(IdGeneratorUuid(), 'output_json_db/events_db.json')
    event_service = EventService(event_repo, user_repository)
    group_repo = GroupRepository(IdGeneratorUuid(), 'output_json_db/groups_db.json')
    group_service = GroupService(group_repo)

    python_devs_group = Group(name="Python Devs Beginners", description="Python Group", user_ids=[], event_ids=[])
    python_group = Group(name="Python Advanced", description="python user group of professionals", user_ids=[],
                         event_ids=[])

    group_service.create(python_group)
    group_service.create(python_devs_group)

    admin11 = User(first_name='Maria', last_name='Georgieva', email="ivo@abc.bg", password="Test123",
                   bio="Passionate Python Dev",
                   is_active=True,
                   role=RoleName.ADMIN, group_id=python_devs_group.id)
    host1 = User(first_name='Ivan', last_name='Petrov', email="ivo@abc.bg", password="Test123",
                 bio="Passionate Python Dev", is_active=True,
                 role=RoleName.HOST, group_id=python_devs_group.id)
    guest1 = User(first_name='Dimitar', last_name='Hristov', email="dimitar@abc.bg", password="Test123",
                  bio="Backend Dev", is_active=True,
                  role=RoleName.GUEST, group_id=python_devs_group.id)

    users = [admin11, guest1, host1]
    for u in users:
        user_service.create(u)
    print("---Users---")
    print_repo_entity(user_repository)

    python_latest_trends = EventMeeting(name="Latest trends of pytthon",
                                        description="Get to know latest trends in clean code",
                                        # creation_date=datetime.fromisoformat('2022-02-22T10:30:00'),
                                        registration_end_date=datetime.fromisoformat('2022-04-22T11:00:00'),
                                        start_datetime=datetime.fromisoformat('2022-04-22T10:30:00'),
                                        end_datetime=datetime.fromisoformat('2022-04-22T18:30:00'),
                                        place="Online",
                                        is_public=True,
                                        capacity=300,
                                        price=0,
                                        creation_user_id=host1.id,
                                        event_status=EventStatusName(EventStatusName.OPEN_FOR_REGISTRATIONS),
                                        registered_user_ids=[])

    event_service.create_event_from_host(host1.id, python_latest_trends)
    # event_service.add_event_post(host1.id, python_latest_trends.id, EventPost(event_id=python_latest_trends.id,
    #                                                                           text="Registrate to our new latest event for python",
    #                                                                           creation_date=datetime.fromisoformat(
    #                                                                               '2022-01-22T10:30:00'),
    #                                                                           creation_user_id=host1.id))
    event_service.send_event_invitation(python_latest_trends.id,
                                        EventInvitation(event_id=python_latest_trends.id,
                                                        user_id=guest1.id,
                                                        sent_date=datetime.fromisoformat('2022-01-23T10:30:00')))
    print(python_group.name)
    found_group: Group = group_service.find_by_name("Python Advanced")
    if found_group is not None:
        found_group.user_ids = [guest1.id]
        found_group.event_ids = [python_latest_trends.id]
        group_service.update(found_group)
    group_service.allow_event_in_group(python_latest_trends.id, python_group.id)
    allowed: bool = group_service.check_event_allowed_group(str(python_group.id), str(python_latest_trends.id))
    print("Allowed event for group: ", allowed)

    print("--- Events -----")
    print_repo_entity(event_repo)

    print("---Groups---")
    print_repo_entity(group_repo)
    # user responds invitation
    # event_service.respond_event_invitation(event_id=python_latest_trends.id,
    #                                        text_response="Many thanks I will participate for sure",
    #                                        response_date=datetime.fromisoformat('2022-01-24T10:30:00'),
    #                                        invitation_response=InvitationResponseTypeName.ACCEPT)
    # guest registers to event
    event_service.register_for_event(event_id=python_latest_trends.id, user_id=guest1.id, is_paid=False)
    event_service.save()
    group_service.save()
    user_service.save()

    user_service.load()
    group_service.load()
    event_service.load()
    print('\n', 'After Loading:')
    print_repo_entity(user_repository.find_all())
    print_repo_entity(event_repo.find_all())
    print_repo_entity(group_repo.find_all())

    root = Tk()
    center_resize_window(root, 800, 400)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    event_controller = EventController(event_service)
    credentials_service = CredentialsService(user_repository)

    credentials_controller = CredentialsController(credentials_service)
    # ivo@abc.bg
    # Test123
    credentials_controller.reload_users()
    credential_view = MainCredentialsView(root,credentials_controller,event_controller)
    credentials_controller.view = credential_view
    root.mainloop()