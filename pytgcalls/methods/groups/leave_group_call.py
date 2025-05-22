import asyncio
from typing import Union

from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...types import NotInGroupCall
from ...types.session import Session


class LeaveGroupCall(Scaffold):
    async def leave_group_call(
        self,
        chat_id: Union[int, str],
    ):
        """Leave a group call

        This method allow to leave a Group Call

        Parameters:
             chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NodeJSNotRunning: In case you try
                to call this method without do
                :meth:`~pytgcalls.PyTgCalls.start` before
            NoActiveGroupCall: In case you try
                to edit a not started group call
            NotInGroupCallError: In case you try
                to leave a non-joined group call

        Example:
            .. code-block:: python
                :emphasize-lines: 10-12

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client)
                app.start()

                ...  # Call API methods

                app.leave_group_call(
                    -1001185324811,
                )

                idle()
        """
        if self._app is not None:
            if self._wait_until_run is not None:
                try:
                    chat_id = int(chat_id)
                except ValueError:
                    chat_id = BridgedClient.chat_id(
                        await self._app.resolve_peer(chat_id),
                    )
                chat_call = await self._app.get_full_chat(
                    chat_id,
                )
                if chat_call is not None:
                    solver_id = Session.generate_session_id(24)

                    async def internal_sender():
                        if not self._wait_until_run.done():
                            await self._wait_until_run
                        await self._binding.send({
                            'action': 'leave_call',
                            'chat_id': chat_id,
                            'type': 'requested',
                            'solver_id': solver_id,
                        })
                    asyncio.ensure_future(internal_sender())
                    result = await self._wait_result.wait_future_update(
                        solver_id,
                    )
                    if isinstance(result, NotInGroupCall):
                        raise NotInGroupCallError()
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
