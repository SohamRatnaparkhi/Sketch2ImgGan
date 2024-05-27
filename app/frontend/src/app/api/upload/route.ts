import { PutObjectCommand, S3Client } from '@aws-sdk/client-s3';
import axios from 'axios';
import fs from 'fs/promises';
import { NextRequest, NextResponse } from "next/server";

export const POST = async (request: NextRequest) => {
    try {
        const { searchParams } = new URL(request.url)
        const filename = searchParams.get('filename')
        const data = await request.formData();
        const file: File | null = data.get('file') as unknown as File;
        const uploadFilePath = process.cwd() + `/src/tmp/uploads/${filename}`;
        console.log(uploadFilePath)
        if (file == null) {
            return NextResponse.json({ message: 'File upload failed' });
        }

        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);

        // write buffer to file
        await fs.writeFile(uploadFilePath, buffer);

        // upload to s3
        const { url } = await uploadToS3(uploadFilePath, filename || "", buffer);
        
        const flaskServer = 'http://localhost:5000/process'
        const {data: flaskServerRes} = await axios.post(flaskServer, {
            imagePath: uploadFilePath
        })

        return NextResponse.json({
            message: 'File uploaded successfully',
            file: {
                name: file.name,
                size: file.size,
                type: file.type,
                path: uploadFilePath,
                relativePath: `/tmp/uploads/${filename}`,
                url: url
            },
            output: flaskServerRes
        });
    } catch (error) {
        console.log(error)
        return NextResponse.json({ message: 'File upload failed' });
    }
}

const uploadToS3 = async (filePath: string, filename: string, file: Buffer): Promise<{
    res: any,
    url: string
}> => {
    const client = new S3Client({
        region: process.env.S3_BUCKET_REGION || "",
        credentials: {
            accessKeyId: process.env.S3_ACCESS_KEY || "",
            secretAccessKey: process.env.S3_SECRET_ACCESS_KEY || "",
        },
    });
    const randomString = Math.random().toString(36).substring(7);
    const command = new PutObjectCommand({
        Bucket: process.env.S3_BUCKET_NAME,
        Key: filename + randomString,
        Body: file,
    });

    try {
        const response = await client.send(command);
        console.log(response);
        return {
            res: response,
            url: `https://${process.env.S3_BUCKET_NAME}.s3.${process.env.S3_BUCKET_REGION}.amazonaws.com/${filename + randomString}`
        };
    } catch (err) {
        console.error(err);
        return {
            res: err,
            url: ""
        };
    }
}