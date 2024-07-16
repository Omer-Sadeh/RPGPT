import {AnimatePresence, motion} from 'framer-motion';
import React from 'react';
import './OverCard.css';

function OverCard({children, show, hideFunc}: {children: any, show: boolean, hideFunc: () => void}) {
    return (
        <>
            <AnimatePresence>
                {show && (
                    <motion.div className="OverCardShadow"
                                initial={{opacity: 0}}
                                animate={{opacity: 1}}
                                exit={{opacity: 0}}
                                onClick={hideFunc}
                    />
                )}
            </AnimatePresence>
            <AnimatePresence>
                {show && (
                    <motion.div className="OverCard"
                                initial={{y: "-100vh"}}
                                animate={{y: 0}}
                                exit={{y: "-100vh"}}
                                transition={{duration: 0.5}}
                    >
                        <div className="OverCardContent">
                            {children}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>

    );
}

export default OverCard;