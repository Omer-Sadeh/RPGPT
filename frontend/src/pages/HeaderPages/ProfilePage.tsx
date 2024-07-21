import React from "react";
import {FilteredValuesGrid} from "../../components/ValuesGrid";
import './ProfilePage.css';
import ImageLoader from "../../components/ImageLoader";

export default function ProfilePage({data, img}: {data: any, img: string}) {
    return (
        <div className="ProfilePage">
            <div className="CharacterName">{data.background.name}</div>
            <ImageLoader bytes={img} alt={"profile"} className={"CharacterImg"} />
            <div className="CharacterBackstory">{data.background.backstory}</div>
            <FilteredValuesGrid values={data.background}
                                filteredOut={["name", "backstory", "traits", "location"]}/>
        </div>
    );
}