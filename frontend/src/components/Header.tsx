import React from 'react';
import './Header.css';
import Button, {HeaderMenuButton} from "./Button";
import ProgressBar from "./ProgressBar";
import { HiLogout } from "react-icons/hi";
import { MdChangeCircle } from "react-icons/md";
import { FaHeart } from "react-icons/fa";
import { FaFortAwesomeAlt } from "react-icons/fa6";

function Header({username, data, cards, unload, logout} : {username: string, data: any, cards: any[], unload: () => void, logout: () => void}) {

    const renderSaveMenu = () => {
        let health = data.data.story.health;

        return (
            <div className="headerSaveMenu">
                <div className="headerSaveMenuButtons">
                    {cards.map((card, index) => {
                        return <HeaderMenuButton text={card.icon} title={card.name} func={card.activation} key={index} notif={card.notif}/>
                    })}
                </div>
                <Button text={<MdChangeCircle />} func={unload} />
                <div className="HealthBar">
                    <div className="HealthBarTitle">{health}/5 <FaHeart /></div>
                    <ProgressBar precentage={(health / 5) * 100} color={"red"}/>
                </div>
            </div>
        );
    }

    return (
        <div className="header">
            <div className="headerTitle"><FaFortAwesomeAlt />RPGPT</div>
            {data.name !== '' && renderSaveMenu()}
            <div className="headerUser">
                <div>{username}</div>
                <Button text={<HiLogout />} func={logout} />
            </div>
        </div>
    );
}

export default Header;