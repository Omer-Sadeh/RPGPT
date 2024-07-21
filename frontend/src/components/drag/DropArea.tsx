import React, {CSSProperties, ReactElement, useEffect, useState} from 'react';
import {CSS} from '@dnd-kit/utilities';
import {DndContext, useDraggable, useDroppable} from "@dnd-kit/core";
import './DropArea.css';
import ClipLoader from "react-spinners/ClipLoader";
import { motion } from 'framer-motion';
import Button from "../Button";
import { SlArrowUp } from "react-icons/sl";

function NewActionCard({hide, add}: { hide: boolean, add: any}) {
    const [editMode, setEditMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const [value, setValue] = useState("")

    useEffect(() => {
        if (hide) {
            setEditMode(false);
            setLoading(false);
            setValue("");
        }
    }, [hide]);

    const handleAdd = async () => {
        if (value === "") {
            setEditMode(false);
            return;
        }
        setLoading(true);

        await add(value).then((result: boolean) => {
            setLoading(false);
            if (result) {
                setEditMode(false);
            } else {
                setValue("");
            }
        }).catch(() => {
            setLoading(false);
            setValue("");
        });
    }

    const renderContent = () => {
        if (editMode) {
            if (loading) {
                return (
                    <div className="actionCardContent actionCardContentCenter" key={"+"}>
                        <ClipLoader
                            color={"aliceblue"}
                            loading={true}
                            size={"15vmin"}
                            aria-label="Loading Spinner"
                            data-testid="loader"
                        />
                    </div>
                );
            }

            return (
                <div className="actionCardContent" key={"+"}>
                    <textarea className="actionCardTextArea" placeholder="Enter new action"
                              value={value} onChange={(e) => setValue(e.target.value)} />
                    <Button text={value !== "" ? "Add" : "Back"} func={handleAdd} />
                </div>
            );
        }
        return (
            <div className="actionCardContent" key={"+"}>
                <div className="actionCardEmpty">+</div>
            </div>
        );
    }

    return (
        <motion.div className={editMode ? "actionCard actionCardNew" : "actionCard"} key={"+"}
                    onClick={editMode ? () => null : () => setEditMode(true)}
                    initial={{opacity: hide ? 1 : 0}}
                    animate={{opacity: hide ? 0 : 1}}
                    transition={{duration: 1}}
                    exit={{opacity: 0}}>
            {renderContent()}
        </motion.div>
    );
}

function Draggable({children, id, hide, dragging}: { children: any, id: any, hide: boolean, dragging: boolean}) {
    const {attributes, listeners, setNodeRef, transform} = useDraggable({id: id});
    const style: CSSProperties = {
        transform: CSS.Translate.toString(transform),
    };

    if (hide) {
        return (
            <motion.div className="actionCard" style={style} key={id}
                        initial={{opacity: 1}} animate={{opacity: 0}} transition={{duration: 1}} exit={{opacity: 0}}>
                {children}
            </motion.div>
        );
    }
    return (
        <motion.div ref={setNodeRef} className="actionCard" style={style} key={id} {...listeners} {...attributes}
                    initial={{opacity: 0}} animate={{opacity: 1}} transition={{duration: 1}} exit={{opacity: 0}}>
            {children}
            {!dragging &&
                <motion.div className="dragTootip"
                            initial={{y: 0}}
                            animate={{y: [0, -10, 0]}}
                            transition={{duration: 1, times: [0, 0.5, 1], repeat: Infinity, ease: "easeInOut"}}
                >
                    <SlArrowUp />
                    <div className="dragTootipText">Drag to choose</div>
                </motion.div>
            }
        </motion.div>
    );
}

function Droppable(props: { id: any; children: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | null | undefined; }) {
    const {isOver, setNodeRef} = useDroppable({
        id: props.id,
    });
    const style = {
        boxShadow: isOver ? "0 0 10px 5px rgba(255, 255, 255, 0.36)" : "none",
    };

    return (
        <div className="actionCardPlaceholder" style={style} ref={setNodeRef}>
            {props.children}
        </div>
    );
}

interface Card {
    key: string;
    content: ReactElement;
}

export default function CardsSet({cards, handleChoose, handleAdd}: { cards: Card[], handleChoose: any, handleAdd: any}) {
    const [parent, setParent] = useState(null);
    const [dragged, setDragged] = useState(null);
    const [dragDeltaY, setDragDeltaY] = useState(0);

    const draggables: any = {}
    const indexToKey: any = {}
    const keyToIndex: any = {}
    cards.forEach((input, index) => {
        if (input.key === "+") {
            draggables[input.key] = <NewActionCard hide={parent !== null} add={handleAdd} />
        } else {
            draggables[input.key] = <Draggable id={index + 1} hide={parent !== null && parent !== input.key} dragging={dragged !== null && dragged === index + 1}>
                {input.content}
            </Draggable>
        }
        indexToKey[index + 1] = input.key;
        keyToIndex[input.key] = index + 1;
    })

    const chooseAction = async (action: string) => {
        await handleChoose(action).then(() => {
            setParent(null);
        });
    }

    return (
        <DndContext onDragEnd={handleDragEnd} onDragMove={handleDragMove}>

            <div className="boardGrid">

                <div className="DropOverlay" style={{opacity: dragDeltaY > 0 ? dragDeltaY / 250 : parent ? 1 : 0}}>
                    <Droppable id="droppable">
                        {parent ? <ClipLoader
                            color={"aliceblue"}
                            loading={true}
                            size={50}
                            aria-label="Loading Spinner"
                            data-testid="loader"
                        /> : '?'}
                    </Droppable>
                </div>

                <div className="cardsGrid" >
                    {Object.keys(draggables).map((draggable) => {
                        return parent !== keyToIndex[draggable] ? draggables[draggable] : null
                    })}
                </div>

            </div>

        </DndContext>
    );

    function handleDragEnd(event: any) {
        setParent(event.over ? event.active.id : null);
        if (event.over) chooseAction(indexToKey[event.active.id]).then();
        setDragDeltaY(0);
        setDragged(null);
    }

    function handleDragMove(event: any) {
        if (event.active.id !== dragged) setDragged(event.active.id);
        setDragDeltaY(-event.delta.y);
    }
}
