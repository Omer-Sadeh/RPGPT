import React, {useEffect, useState} from 'react';
import './GoalsPage.css';
import API from "../../services/API";
import {AnimatePresence, motion} from 'framer-motion';
import Button, {BigButton} from "../../components/Button";
import { LuRefreshCw } from "react-icons/lu";
import AUTH from "../../services/auth";

function GoalCard({goal, func, active} : {goal: any, func: any, active: boolean}) {
    return (
        <motion.div layoutId={goal.goal} onClick={() => active ? func(goal) : null}
                    className={active ? "GoalCard act" : "GoalCard"}
                    initial={{ opacity: active ? 0.1 : 1 }}
                    animate={{ opacity: active ? 1 : 0.1 }}
                    whileHover={{ scale: active ? 1.01 : 1 }}
                    exit={{ opacity: 0 }}
        >
            {typeof goal.title === 'string' ?
                <motion.h5>{goal.title}</motion.h5> :
                <motion.h1>{goal.title}</motion.h1>
            }
        </motion.div>
    );

}

function GoalsPage({saveName}: { saveName: string }) {
    const [loading, setLoading] = useState(true);
    const [goals, setGoals] = useState<any[]>([]);
    const [selectedId, setSelectedId] = useState<any>(null);

    useEffect(() => {
        getGoals(false).then();
        // eslint-disable-next-line
    }, []);

    const getGoals = async (regen: boolean) => {
        setLoading(true);
        setGoals([]);
        await API.goals(AUTH.getToken(), saveName, regen).then((data) => {
            for (let i = 0; i < 5; i++) {
                setGoals((goals) => [...goals, data[i]]);
            }
            setLoading(false);
        }).catch(() => {
            setLoading(false);
        });
    }

    const newStory = (goal: string) => {
        API.newStory(AUTH.getToken(), saveName, goal).catch((error) => {
            console.log("Failed to start new story: " + error.message);
        });
    }

    const renderGoalsScreen = () => {
        if (loading) {
            return (
                <div className="GoalsContainer">
                    {
                        Array.from({length: 6}, (_, i) => (
                            <GoalCard goal={{title: "Loading..."}} func={() => null} active={false} key={i}/>
                        ))
                    }
                </div>
            );
        } else {
            return (
                <div className="GoalsContainer">
                    {goals.map((goal) => (
                        <GoalCard goal={goal} func={setSelectedId} active={selectedId === null} key={goal.title}/>
                    ))}
                    {goals.length < 5 && (
                        Array.from({length: 5 - goals.length}, (_, i) => (
                            <GoalCard goal={{title: "no goal found!"}} func={() => null} active={false} key={i}/>
                        ))
                    )}
                    <GoalCard
                        goal={{title: <LuRefreshCw />}}
                        func={() => getGoals(true)}
                        active={selectedId === null}
                        key={"regen"}
                    />

                    <AnimatePresence>
                        {selectedId && (
                            <motion.div layoutId={selectedId.goal} className="GoalOpenCard">
                                <motion.h5>{selectedId.goal}</motion.h5>
                                <motion.div className="reward-text">Rewards on completion:</motion.div>
                                {selectedId.gold_reward > 0 &&
                                    <motion.div className="gold-text">Gold: {selectedId.gold_reward}</motion.div>}
                                {selectedId.xp_reward > 0 &&
                                    <motion.div className="xp-text">XP: {selectedId.xp_reward}</motion.div>}
                                {selectedId.gold_reward === 0 && selectedId.xp_reward === 0 &&
                                    <motion.div className="noreward-text">None!</motion.div>}
                                <BigButton func={() => newStory(selectedId.goal)} text={"Choose"}/>
                                <div className="x-button">
                                    <Button func={() => setSelectedId(null)} text={"X"}/>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            );
        }
    }

    return (<>
        <div className="noStoryText">
            <h1>No Active adventure!</h1>
            <h3>Choose an adventure to start your story:</h3>
        </div>
        {renderGoalsScreen()}
    </>);
}

export default GoalsPage;