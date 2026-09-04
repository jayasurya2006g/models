# ANPR test images

Put a real vehicle image with a clearly visible number plate in this directory,
then upload it to `POST /anpr/image` in Swagger. The service never invents OCR
results. Without trained model files in `weights/`, ANPR cannot perform a
detection; it will report the existing processing error so the missing model is
visible rather than returning fake data.