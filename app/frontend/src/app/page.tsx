"use client";

import { ButtonDestructive } from "@/components/Uploader/ButtonDestructinve";
import axios from "axios";
import { useRef, useState } from "react";
import { FileUploader } from "react-drag-drop-files";
import { Bars } from "react-loader-spinner";

export default function Home() {
  const [file, setFile] = useState(null);
  const [loader, setLoader] = useState(false)
  const inputFileRef = useRef<HTMLInputElement>(null)
  const outputImageRef = useRef<HTMLImageElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const [output, setOutput] = useState<string | null>("")
  const [uploadedImagePath, setUploadedImagePath] = useState<string | null>(null)
  const handleChange = (file: any) => {
    setFile(file);
  };
  console.log(loader)
  const uploadFileHandler = async () => {
    if (!file) return
    setLoader(true)
    const form = new FormData()
    form.append('file', file)
    const { data } = await axios.post(`/api/upload?filename=${"img"}.png`, form, {
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
      setLoader(false)
    }
  }

  return (
    <div className="h-screen w-screen bg-white flex justify-center items-center text-center">
      <div className="p-3 flex flex-col justify-center h-3/4 w-3/4 bg-slate-600">
        <div className="bg-orange-500 p-3 h-1/5">
          <p className="text-4xl">
            Transforming strokes of imagination into vibrant pixels of reality!
          </p>
        </div>
        <div className="flex flex-row bg-white h-4/5 justify-center">
          <div className="flex-auto w-1/2 flex justify-center items-center p-4 m-4 bg-gray-50">
            {<div>
              <FileUploader handleChange={handleChange} name="file" />
              <img ref={imageRef} alt="uploaded image" />
            </div>}
          </div>
          <div className="flex-auto flex w-1/2 justify-center items-center p-4 m-4 bg-gray-50">
            <div>
              <img ref={outputImageRef} alt="uploaded image" />
              {
                loader && <Bars
                  height="80"
                  width="80"
                  color="#4fa94d"
                  ariaLabel="bars-loading"
                  wrapperStyle={{}}
                  wrapperClass=""
                  visible={true}
                />
              }
            </div>
          </div>
        </div>
        <div className="w-full">

          <ButtonDestructive onClick={uploadFileHandler} title="Submit" />
        </div>
      </div>
    </div>
  );
}

{/* <InputFile /> */ }