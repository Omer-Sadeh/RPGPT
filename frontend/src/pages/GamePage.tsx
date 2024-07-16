import { motion } from 'framer-motion';
import React from 'react';
import './GamePage.css';
import GoalsPage from "./GamePages/GoalsPage";
import AdventurePage from "./GamePages/AdventurePage";

function GamePage({save, data} : {save: string, data: any}) {
    return (
        <motion.div className="GamePage" initial={{scale: 0}}
                    animate={{scale: 1}}
                    transition={{
                        duration: 1.5
                    }}>
            {(Object.keys(data.story).length === 0) ?
                <GoalsPage saveName={save}/> :
                <AdventurePage saveData={data} saveName={save}/>
            }
        </motion.div>
    );
}

export default GamePage;