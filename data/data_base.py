import psycopg2
from app.config.bot_config import get_config
import os


class BdPlannerTasks():

    section = 'data_base'
    conn = psycopg2.connect(
        database="planner_task",
        user=get_config(section, 'user'),
        password=get_config(section, 'password'),
        host=get_config(section, 'host'),
        port=get_config(section, 'port'))

    async def commit_query(self, query, many=False, commit=False, conn=conn):
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if commit:
                    conn.commit()
                elif many:
                    return cur.fetchall()
                else:
                    return cur.fetchone()

    async def set_user(self, user_id, ):
        query = f'''
                INSERT INTO scheduled_tasks(user_id)
                VALUES({user_id})
                '''
        await self.commit_query(query, commit=True)

    async def set_data(self, user_id, datetime, task, conn=conn):
        query = f'''
                INSERT INTO scheduled_tasks(user_id, datetime, task)
                VALUES({user_id},'{datetime}','{task}')
                '''
        await self.commit_query(query, commit=True)

    async def update_recall(self, user_id, datetime, task_name):
        query = f"""
                UPDATE scheduled_tasks SET recall = '{datetime}'
                WHERE user_id = {user_id} AND task = '{task_name}'
                """
        await self.commit_query(query, commit=True)

    async def update_complete(self, user_id, complete):
        query = f'''
                UPDATE scheduled_tasks SET complete = {complete}
                WHERE user_id = {user_id}
                '''
        await self.commit_query(query, commit=True)

    async def get_user(self, user_id):
        query = f'''
                SELECT user_id FROM scheduled_tasks
                WHERE user_id = {user_id}
                '''
        return await self.commit_query(query)

    async def get_tasks(self, user_id, date=None, name_task=None, conn=conn):
        select = ' SELECT task, complete FROM scheduled_tasks\n'
        if name_task is not None:
            where = f"""WHERE task = '{name_task}'
                        AND datetime = '{date}'
                        AND user_id = {user_id}"""
        else:
            where = f"WHERE datetime ='{date}' AND user_id = {user_id}"
        query = select + where
        return await self.commit_query(query, True)

    async def get_task_on_recall(self, user_id, datetime_recall):
        query = f"""
                SELECT task, datetime FROM scheduled_tasks
                WHERE user_id = {user_id} AND recall = '{datetime_recall}'
                """

        return await self.commit_query(query, True)

    async def get_list_date(self, user_id):
        query = f'''
                SELECT DISTINCT datetime FROM scheduled_tasks
                WHERE user_id = {user_id}
                '''
        return await self.commit_query(query, True)

    async def get_icon_task(self):
        query = 'SELECT complete, url FROM icons_task'
        return await self.commit_query(query, True)


if __name__ == '__main__':
    os.chdir('..')
