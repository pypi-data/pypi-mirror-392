import asyncio
from typing import Dict, Union
from loguru import logger
from ..client.game_client import GameClient





class WheelOfAffluence(GameClient):
    
    
    async def spin_woa(
        self,
        sync: bool = True
    ) -> Union[Dict, bool]:
        
        """
        Spin the Wheel Of Affluence.
        
        Args:
            sync: Whether to wait for server response
            
        Returns:
            Server response dictionary if sync=True and successful,
            True if async and successful, False on error
        """
        
        try:
            
            wof_data = {"LWET":1}
            if sync:
                return await self.send_rpc("lws", wof_data)
            
            else:
                await self.send_json_message("lws", wof_data)
                return True
        
        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for spining wof response")
            return False
        except ConnectionError as e:
            logger.error(f"Connection error while spining wof : {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while spining wof: {e}")
            return False
        
        
        
    async def auto_spin_woa(
        self,
        tickets: int,
    ) -> None:
        
        """
        Autospin for Wheel Of Affluence.
        
        Args:
            tickets: number of tickets (int).
        
        
        """
        if tickets <= 0:
            logger.warning("Not enough tickets!")
            return
        
        for i in range(tickets):
            logger.info(f"Spinning ticket {i + 1}/{tickets}")
            
            result = await self.spin_woa(sync=True)
            
            if result is False:
                logger.error(f"Spin {i + 1} failed, stopping autospin.")
                break
            
            await asyncio.sleep(0.4)
        
        logger.success("All woa spins done!")
            
        