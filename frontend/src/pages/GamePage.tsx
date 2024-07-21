import { motion } from 'framer-motion';
import React, {useState} from 'react';
import './GamePage.css';
import API from "../services/API";
import AUTH from "../services/auth";
import {BigButton} from "../components/Button";
import ImageLoader from "../components/ImageLoader";
import DropArea from "../components/drag/DropArea";
import { IoSkullOutline } from "react-icons/io5";
import { LuCrown } from "react-icons/lu";

function GamePage({save, data, sceneImg, endGame} : {save: string, data: any, sceneImg: string, endGame: any}) {
    const [result, setResult] = useState("");
    const [resExp, setResExp] = useState(0);

    const updateResult = (res: string, rewardXp: number) => {
        setResult(res);
        if (res === "Success") {
            setResExp(rewardXp);
        } else {
            setResExp(0);
        }
    }

    const chooseAction = async (action: string) => {
        let rewardXp = data.story.experience[data.story.options.indexOf(action)];
        await API.advance(AUTH.getToken(), save, action).then((res) => {
            updateResult(res, rewardXp);
            console.log("action result: " + res);
        }).catch((error) => {
            console.error(error.message);
        });
    }

    const newAction = async (newAction: string) => {
        return await API.newOption(AUTH.getToken(), save, newAction).then(() => {
            return true;
        }).catch(() => {
            return false;
        });
    }

    const renderSceneText = () => {
        if (data.story.scene === "") {
            return <span>Welcome to the Adventure!</span>;
        } else if (result === "") {
            return <span>{data.story.scene}</span>;
        } else {
            if (result === "Success") {
                return <span><span className="success">[ Success! +{resExp}XP ]</span> {data.story.scene}</span>;
            } else {
                return <span><span className="fail">[ Failure! ]</span> {data.story.scene}</span>;
            }
        }
    }

    const renderGameEnd = () => {
        let death = data.story.health === 0;
        let message = death ? "Game Over! You have died." : "Congratulations! You have completed the adventure!";
        let icon = death ? <IoSkullOutline size={"10vmin"} /> : <LuCrown size={"10vmin"} />;

        return <>
            {icon}
            <h3>{message}</h3>
            <BigButton text={"Continue"} func={endGame} />
        </>
    }

    const generateCards = () => {
        let cards = data.story.options.map((option: string, index: number) => {
            let rate = data.story.rates[index];
            let advRate = rate + (1 - rate) * 0.75;
            let advSkill = data.story.advantages[index];
            let advLevel = data.story.levels[index];
            let xp = data.story.experience[index];
            let advReached = data.skills[advSkill] >= advLevel;

            let component = <div className="actionCardContent">
                <div className="actionCardValue">{option}</div>
                <div className="actionCardStats">
                    <div>{data.story.rates[index] * 100}% success rate</div>
                    <div className={advReached ? "actionCardAdv reached" : "actionCardAdv"}>({advRate * 100}% with {advSkill} level {advLevel})</div>
                    <div className="actionCardXp">+{xp} XP</div>
                </div>
            </div>
            return {key: option, content: component};
        });
        if (data.story.options.length < 5) cards.push({key: "+", content: null});
        return cards;
    }

    return (
        <motion.div className="GamePage" initial={{opacity: 0}}
                    animate={{opacity: 1}}
                    transition={{duration: 1.5}}>
            <div className="adventureContainer">
                <div className="adventureScene">
                    <div className="sceneImgCon">
                        <ImageLoader bytes={sceneImg} alt={"sceneImage"} className={"sceneImg"}/>
                        <div className="sceneLocationText">{data.background.location}</div>
                    </div>

                    <div className="sceneText">
                        {renderSceneText()}
                    </div>
                </div>

                <div className="adventureOptions">
                    {data.story.options.length > 0 ?
                        <DropArea cards={generateCards()} handleChoose={chooseAction} handleAdd={newAction}/> :
                        renderGameEnd()}
                </div>
            </div>
        </motion.div>
    );
}

export default GamePage;