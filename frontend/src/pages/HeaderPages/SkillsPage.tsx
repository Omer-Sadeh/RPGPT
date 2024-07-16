import React from "react";
import {ClickableValuesGrid, ValuesGrid} from "../../components/ValuesGrid";
import API from "../../services/API";
import ProgressBar from "../../components/ProgressBar";
import './SkillsPage.css';
import AUTH from "../../services/auth";

export default function SkillsPage({saveData, save_name} : {saveData: any, save_name: string}) {
    const renderSkills = () => {
        if (saveData.action_points === 0) {
            return <ValuesGrid values={saveData.skills}/>;
        } else {
            return <>
                <ClickableValuesGrid values={saveData.skills} onClick={(skill: string) => {
                    API.spendSkill(AUTH.getToken(), skill, save_name).catch((error) => {
                        console.error("Error spending skill: " + error.message);
                    });
                }}/>
                <div className="ActionPoints">Available Skill Points: {saveData.action_points}</div>
            </>;
        }
    }

    return (
        <div className="SkillsPage">
            <div className="SkillsTitle">Level: {saveData.level}</div>
            <div className="xpSubTitle">{saveData.xp} / {saveData.xp_to_next_level} XP</div>
            <div className="xpbar"><ProgressBar precentage={saveData.xp / saveData.xp_to_next_level * 100}/></div>
            {renderSkills()}
        </div>
    );
}