from .auth.views import router as auth_router
from .rules.views import role_router
from .departments.views import router as department_router
from .rules.views import permission_router
from .blocks.views import router as block_router
from .wells.views import router as well_router
from .shifts.views import router as shift_router
from .notifications.views import router as notification_router
from .tasks.views import router as task_router
from .task_comments.views import router as task_comment_router
from .task_checklist.views import router as task_checklist_router
from .task_files.views import router as task_file_router
from .users.views import router as user_router
from .lvl4_act.views import router as lvl4_act_router
from .ai.views import router as ai_router
from .reshift.views import router as reshift_router

def get_routes(app):
    app.include_router(auth_router)
    app.include_router(department_router)
    app.include_router(shift_router)
    app.include_router(role_router)
    app.include_router(permission_router)
    app.include_router(block_router)
    app.include_router(well_router)
    app.include_router(notification_router)
    app.include_router(task_router)
    app.include_router(task_comment_router)
    app.include_router(task_checklist_router)
    app.include_router(task_file_router)
    app.include_router(user_router)
    app.include_router(lvl4_act_router)
    # app.include_router(ai_router)
    app.include_router(reshift_router)

    return app
