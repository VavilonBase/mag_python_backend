from database import ProjectOrm, new_session
from sqlalchemy import select
from schemas import SProject, SProjectFullAdd
from datetime import date

class ProjectRepository:
    @classmethod
    async def add_project(cls, project: SProjectFullAdd) -> int:
        async with new_session() as session:
            data = project.model_dump()
            new_task = ProjectOrm(**data)
            session.add(new_task)
            await session.flush()
            await session.commit()
            return new_task.id
    
    @classmethod
    async def get_projects(cls) -> list[SProject]:
        async with new_session() as session:
            query = select(ProjectOrm)
            result = await session.execute(query)
            project_models = result.scalars().all()
            projects = [SProject.model_validate(project_model) for project_model in project_models]
            return projects
        
    @classmethod
    async def get_project(cls, number, author) -> SProject | None:
        async with new_session() as session:
            query = select(ProjectOrm).where(ProjectOrm.number == number).where(ProjectOrm.author == author)
            result = await session.execute(query)
            project_models = result.scalars().all()
            projects = [SProject.model_validate(project_model) for project_model in project_models]
            if len(projects) > 0:
                return projects[0]
            else:
                return None
