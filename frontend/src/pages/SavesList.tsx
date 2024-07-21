import React from 'react';
import './SavesList.css';
import Button from "../components/Button";
import { motion } from "framer-motion";
import { FaTrashAlt } from "react-icons/fa";
import ImageLoader from "../components/ImageLoader";

const container = {
    hidden: { opacity: 1, scale: 0 },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            delayChildren: 0.3,
            staggerChildren: 0.2
        }
    }
};

const item = {
    hidden: { y: 20, opacity: 0 },
    visible: {
        y: 0,
        opacity: 1
    }
};

function SavesList({saves, loadSave, newSave, deleteSave} : {saves: any, loadSave: (save: string) => void, newSave: () => void, deleteSave: (save: string) => void}) {

    const Card = ({children, func} : {children: any, func: () => void}) =>
        <motion.div className="card" whileHover={{scale: 1.02}} whileTap={{scale: 0.98}} onClick={func}>{children}</motion.div>

    const renderSaves = () => {
        return Object.keys(saves).slice(0, 4).map((save) => (
            <motion.li key={saves[save].id} className="item" variants={item}>
                <Card func={() => loadSave(saves[save].id)}>
                    <ImageLoader bytes={saves[save].image} alt={"character"} className={"cardImg"} />
                    <div className="cardText">{saves[save].name}</div>
                </Card>
                <div className="space"/>
                <Button text={<FaTrashAlt />} func={() => deleteSave(saves[save].id)}/>
            </motion.li>
        ));
    }

    const renderNewSave = () => {
        if (saves.length >= 4) return null;
        return <motion.li key={"new"} className="item" variants={item}>
                <Card func={newSave}>
                    <span className="plus">+</span>
                </Card>
            </motion.li>;
    }

    const renderPlaceholders = () => {
        let placeholders = 3 - saves.length;
        return placeholders > 0 ? Array(placeholders).fill(0).map((_, index) => (
            <motion.li key={index} className={"empty" + index} variants={item}>
                <div className="card cardEmpty">
                </div>
            </motion.li>
        )) : null;
    }

    return (
        <div className="container">
            <h1>Choose a character:</h1>
            <motion.ul className="list-container" variants={container} initial="hidden" animate="visible">
                {renderSaves()}
                {renderNewSave()}
                {renderPlaceholders()}
            </motion.ul>
        </div>
    );
}

export default SavesList;