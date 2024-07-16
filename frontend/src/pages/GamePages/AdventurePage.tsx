import React, {useEffect, useState} from 'react';
import './AdventurePage.css';
import {BigButton} from "../../components/Button";
import API from "../../services/API";
import ImageLoader from "../../components/ImageLoader";
import DropArea from "../../components/drag/DropArea";
import AUTH from "../../services/auth";

function AdventurePage({saveData, saveName}: { saveData: any, saveName: string }) {
    const [result, setResult] = useState("");
    const [resExp, setResExp] = useState(0);
    const [sceneImg, setSceneImg] = useState("");

    useEffect(() => {
        updateSceneImg().then();
        // eslint-disable-next-line
    }, [saveData]);

    const updateSceneImg = async () => {
        await API.getImage(AUTH.getToken(), saveName, 'scene').then((res) => {
            setSceneImg(res);
        }).catch((error) => {
            console.error(error.message);
        });
    }

    const updateResult = (res: string, rewardXp: number) => {
        setResult(res);
        if (res === "Success") {
            setResExp(rewardXp);
        } else {
            setResExp(0);
        }
    }

    const chooseAction = async (action: string) => {
        let rewardXp = saveData.story.experience[saveData.story.options.indexOf(action)];
        await API.advance(AUTH.getToken(), saveName, action).then((res) => {
            updateResult(res, rewardXp);
        }).catch((error) => {
            console.error(error.message);
        });
    }

    const newAction = async (newAction: string) => {
        return await API.newOption(AUTH.getToken(), saveName, newAction).then(() => {
            return true;
        }).catch(() => {
            return false;
        });
    }

    const endGame = async () => {
        await API.endGame(AUTH.getToken(), saveName).catch((error) => {
            console.error(error.message);
        });
    }

    const renderSceneText = () => {
        if (saveData.story.scene === "") {
            return <span>Welcome to the Adventure!</span>;
        } else if (result === "") {
            return <span>{saveData.story.scene}</span>;
        } else {
            if (result === "Success") {
                return <span><span className="success">[ Success! +{resExp}XP ]</span> {saveData.story.scene}</span>;
            } else {
                return <span><span className="fail">[ Failure! ]</span> {saveData.story.scene}</span>;
            }
        }
    }

    const renderGameEnd = () => {
        return <>
            {saveData.story.health === 0 ? <h3>Game Over! You have died.</h3> :
                <h3>Congratulations! You have completed the adventure!</h3>}
            <BigButton text={"Continue"} func={endGame} />
        </>
    }

    const generateCards = () => {
        let cards = saveData.story.options.map((option: string, index: number) => {
            let rate = saveData.story.rates[index];
            let advRate = rate + (1 - rate) * 0.75;
            let advSkill = saveData.story.advantages[index];
            let advLevel = saveData.story.levels[index];
            let xp = saveData.story.experience[index];
            let advReached = saveData.skills[advSkill] >= advLevel;

            let component = <div className="actionCardContent">
                <div className="actionCardValue">{option}</div>
                <div className="actionCardStats">
                    <div>{saveData.story.rates[index] * 100}% success rate</div>
                    <div className={advReached ? "actionCardAdv reached" : "actionCardAdv"}>({advRate * 100}% with {advSkill} level {advLevel})</div>
                    <div className="actionCardXp">+{xp} XP</div>
                </div>
            </div>
            return {key: option, content: component};
        });
        if (saveData.story.options.length < 5) cards.push({key: "+", content: null});
        return cards;
    }

    return (
        <div className="adventureContainer">

            <div className="adventureScene">
                <div className="sceneImgCon">
                    <ImageLoader bytes={sceneImg} alt={"sceneImage"} className={"sceneImg"} />
                    <div className="sceneLocationText">{saveData.background.location}</div>
                </div>

                <div className="sceneText">
                    {renderSceneText()}
                </div>
            </div>

            <div className="adventureOptions">
                {saveData.story.options.length > 0 ?
                    <DropArea cards={generateCards()} handleChoose={chooseAction} handleAdd={newAction} /> :
                    renderGameEnd()}
            </div>
        </div>
    );
}

export default AdventurePage;