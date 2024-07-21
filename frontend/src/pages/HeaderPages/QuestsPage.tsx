import React from "react";
import './QuestsPage.css';
import {AnimatePresence, motion} from "framer-motion";
import { FaEye, FaEyeSlash } from "react-icons/fa";

function Goal({goal} : {goal: any}) {
    const [showGoal, setShowGoal] = React.useState(false);

    if (goal.status !== "Active") {
        return <div className="GoalContainer">
            <div className="GoalTitleStrike">{goal.title}</div>
        </div>;
    }

    return <div className="GoalContainer">
        <div className="GoalTitle" onClick={() => setShowGoal(!showGoal)}>{goal.title}
            <span className="GoalVisibilityIcon">
                {showGoal ? <FaEye />: <FaEyeSlash /> }
            </span>
        </div>
        <AnimatePresence>
            {showGoal && <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="GoalDetailsContainer"
            >
                <div className="GoalDescription">{goal.description}</div>
                <div className="GoalRewards">
                    <span className="XpReward">XP: {goal.xp_reward}</span>
                    {goal.gold_reward > 0 && <span className="GoldReward">Gold: {goal.gold_reward}</span>}
                </div>
            </motion.div>}
        </AnimatePresence>
    </div>;
}

export default function QuestsPage({saveData} : {saveData: any}) {
    return (
        <div className="QuestsPage">
            <div className="QuestsPageTitle">Quest</div>
            <div className="QuestContainer">
                <div className="QuestTitle">{saveData.quest.quest_title}</div>
                <div className="QuestDescription">{saveData.quest.quest_description}</div>
                <div className="QuestRewards">
                    <span className="XpReward">XP: {saveData.quest.quest_xp_reward}</span>
                    {saveData.quest.quest_gold_reward > 0 && <span className="GoldReward">Gold: {saveData.quest.quest_gold_reward}</span>}
                </div>
            </div>

            <div className="QuestsPageSubTitle">Goals</div>
            {Object.values(saveData.quest.goals).map((goal: any) => <Goal goal={goal} key={goal.title} />)}
        </div>
    );
}