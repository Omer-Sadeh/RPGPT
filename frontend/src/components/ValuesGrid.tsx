import { motion } from 'framer-motion';
import React from 'react';
import './ValuesGrid.css';

function GridItem({name, value} : {name: string, value: any}) {
    return (
        <div className="values-item">
            <div className="values-item-value">{value}</div>
            <div className="values-item-key">{name}</div>
        </div>
    );
}

function ClickableGridItem({name, value, onClick} : {name: string, value: any, onClick: any}) {
    return (
        <div className="values-item" onClick={onClick}>
            <motion.div className="values-clickable"
                whileHover={{scale: 1.1}}
                whileTap={{scale: 0.95}}
                transition={{type: "spring", stiffness: 300, damping: 30}}>
                <div className="values-item-value">{value}</div>
                <div className="values-item-key">{name}</div>
            </motion.div>
        </div>
    );
}

function UnlabeledClickableGridItem({value, onClick} : {value: any, onClick: any}) {
    return (
        <div className="values-item" onClick={onClick}>
            <motion.div className="values-clickable values-item-big"
                        whileHover={{scale: 1.1}}
                        whileTap={{scale: 0.95}}
                        transition={{type: "spring", stiffness: 300, damping: 30}}>
                <div className="values-item-value">{value}</div>
            </motion.div>
        </div>
    );
}

function FillableGridItem({name, value, onClick} : {name: string, value: any, onClick: any}) {
    return (
        <div className="values-item" onClick={() => onClick(name)}>
            <motion.div className="values-clickable"
                        whileHover={{scale: 1.1}}
                        whileTap={{scale: 0.95}}
                        transition={{type: "spring", stiffness: 300, damping: 30}}>
                {value !== "" ? <div className="values-item-value">{value}</div> :
                <div className="values-item-value empty-value">Click To Choose</div>}
                <div className="values-item-key">{name}</div>
            </motion.div>
        </div>
    );
}

export function FilteredValuesGrid({values, filteredOut}: { values: any, filteredOut: string[]}) {
    return (
        <div className="values-grid">
            {Object.keys(values).sort().filter(key => !filteredOut.includes(key)).map((key, index) => {
                return <GridItem key={index} name={key} value={values[key]}/>;
            })}
        </div>
    );
}

export function FillableFilteredValuesGrid({values, filteredOut, onClick} : {values: any, filteredOut: string[], onClick: any}) {
    return (
        <div className="values-grid">
            {Object.keys(values).filter(key => !filteredOut.includes(key)).sort().map((key, index) => {
                return <FillableGridItem key={index} name={key} value={values[key]} onClick={() => onClick(key)}/>;
            })}
        </div>
    );
}

export function ClickableFilteredValuesGrid({values, filteredOut, onClick} : {values: any, filteredOut: string[], onClick: any}) {
    return (
        <div className="values-grid">
            {Object.keys(values).filter(key => !filteredOut.includes(key)).sort().map((key, index) => {
                return <ClickableGridItem key={index} name={key} value={values[key]} onClick={() => onClick(key)}/>;
            })}
        </div>
    );
}

export function UnlabeledClickableFilteredValuesGrid({values, filteredOut, onClick} : {values: string[], filteredOut: string[], onClick: any}) {
    return (
        <div className="values-grid">
            {values.filter(key => !filteredOut.includes(key)).sort().map((key, index) => {
                return <UnlabeledClickableGridItem key={index} value={key} onClick={() => onClick(key)}/>;
            })}
        </div>
    );
}

export function ValuesGrid({values} : {values: any}) {
    return <FilteredValuesGrid values={values} filteredOut={[]}/>;
}

export function ClickableValuesGrid({values, onClick} : {values: any, onClick: any}) {
    return <ClickableFilteredValuesGrid values={values} filteredOut={[]} onClick={onClick}/>;
}

export function UnlabeledClickableValuesGrid({values, onClick} : {values: any, onClick: any}) {
    return <UnlabeledClickableFilteredValuesGrid values={values} filteredOut={[]} onClick={onClick}/>;
}

export default ValuesGrid;