@echo off
echo Removing PDF Optimizer Registry Keys...

reg delete "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer150" /f
reg delete "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer200" /f
reg delete "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer300" /f

echo.
echo Done.
pause
