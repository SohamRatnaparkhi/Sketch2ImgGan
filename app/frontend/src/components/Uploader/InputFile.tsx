"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import axios from "axios";
import { useRef, useState } from "react";
import { ButtonDestructive } from "./ButtonDestructinve";

export function InputFile() {
    // const [file, setFile] = useState<File | null>(null)
    const inputFileRef = useRef<HTMLInputElement>(null)
    const outputImageRef = useRef<HTMLImageElement>(null)
    const imageRef = useRef<HTMLImageElement>(null)
    const [uploadedImagePath, setUploadedImagePath] = useState<string | null>(null)
    const [output, setOutput] = useState<string | null>("")

    const uploadFileHandler = async () => {
        const file = inputFileRef.current?.files?.[0]
        if (!file) return
        const form = new FormData()
        form.append('file', file)
        const { data } = await axios.post(`/api/upload?filename=${file.name}`, form, {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        })
        console.log(data)
        if (imageRef.current) {
            console.log(data.file.url)
            imageRef.current.src = data.file.url
        }
        setOutput(data.output.s3Link)
        setUploadedImagePath(data.file.path)

        if (outputImageRef.current) {
            outputImageRef.current.src = data.output.s3Link
        }
    }

    return (
        <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="picture">Picture</Label>
            <Input id="picture" type="file" ref={inputFileRef} />
            <ButtonDestructive onClick={uploadFileHandler} title="Submit" />

            <img ref={imageRef} alt="uploaded image" />
            
            <img ref={outputImageRef} alt="uploaded image" />

            {/* <img src="https://git-store-bucket-final.s3.ap-south-1.amazonaws.com/Screenshot from 2024-05-11 13-28-07.pngxrlo04" alt="" /> */}
        </div>
    )
}
