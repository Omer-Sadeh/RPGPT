import React from 'react';
import './Button.css';
import {motion} from "framer-motion";

export function Button({text, func} : {text: any, func: () => any}) {
    return (
        <motion.button className="button" onClick={func} whileTap={{scale: 0.9}}>{text}</motion.button>
    );
}

export function ToggleButton({text, func, active}: { text: string, func: () => any, active: boolean}) {
    return (
        <motion.button className={active ? "button" : "button toggle-inactive"} onClick={func} whileTap={{scale: 0.9}}>{text}</motion.button>
    );
}

export function BigButton({text, func} : {text: string, func: () => any}) {
    return (
        <motion.button className="button big" onClick={func} whileTap={{scale: 0.9}}>{text}</motion.button>
    );
}

export function BigButtonActived({text, func, active} : {text: string, func: () => any, active: boolean}) {
    return (
        <motion.button className={active ? "button big" : "button big big-inactive"} onClick={active ? func : () => {}} whileTap={{scale: 0.9}}>{text}</motion.button>
    );
}

export function HeaderMenuButton({text, title, func, notif} : {text: any, title: string, func: () => any, notif: boolean}) {
    return (
        <motion.button className="button" onClick={func} whileTap={{ scale: 0.9 }} title={title}
                       initial={{ scale: 1 }}
                       animate={notif ? {scale: [1, 1.1, 1, 1, 1, 1],} : {}}
                       transition={{
                           duration: notif ? 1 : 0.2,
                           ease: "easeInOut",
                           times: notif? [0, 0.2, 0.4, 0.6, 0.8, 1] : [],
                           repeat: notif ? Infinity : 0,
                           repeatDelay: 0
                       }}>
            {text}
        </motion.button>
    );
}

export default Button;