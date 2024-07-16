import React from 'react';
import {AnimatePresence, motion} from "framer-motion";

function FadeScreen({children, show, classname} : {children: any, show: boolean, classname: string}) {
    return (
        <AnimatePresence>
            {show &&
                <motion.div className={classname} initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}}>
                    {children}
                </motion.div>
            }
        </AnimatePresence>);
}

export default FadeScreen;
