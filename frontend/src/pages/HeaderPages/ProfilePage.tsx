import React, {useEffect, useState} from "react";
import {FilteredValuesGrid} from "../../components/ValuesGrid";
import './ProfilePage.css';
import API from "../../services/API";
import ImageLoader from "../../components/ImageLoader";
import AUTH from "../../services/auth";

export default function ProfilePage({save, data}: {save: string, data: any}) {
    const [imgString, setImgString] = useState<string>("");

    useEffect(() => {
        API.getImage(AUTH.getToken(), save, 'character').then((data) => {
            setImgString(data);
        }).catch(() => {
            setImgString("");
        });
        // eslint-disable-next-line
    }, []);

    return (
        <div className="ProfilePage">
            <div className="CharacterName">{data.background.name}</div>
            <ImageLoader bytes={imgString} alt={"profile"} className={"CharacterImg"} />
            <div className="CharacterBackstory">{data.background.backstory}</div>
            <FilteredValuesGrid values={data.background}
                                filteredOut={["name", "backstory", "traits", "location"]}/>
        </div>
    );
}