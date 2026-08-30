import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileText, Loader2, X, RefreshCw } from 'lucide-react';

export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

interface PDFDropzoneProps {
  id: string;
  label?: string;
  sublabel?: string;
  accept?: string;
  maxSizeMB?: number;
  currentFile: File | null;
  isLoading: boolean;
  loadingText?: string;
  onFileSelected: (file: File) => void;
  onError?: (errorMessage: string) => void;
  onClear?: () => void;
  accentColor?: 'cyan' | 'blue';
  disabled?: boolean;
}

export const PDFDropzone: React.FC<PDFDropzoneProps> = ({
  id,
  label = 'Click to select or drag PDF file here',
  sublabel = 'Supports PDF format only (Max 10MB)',
  accept = '.pdf,application/pdf',
  maxSizeMB = 10,
  currentFile,
  isLoading,
  loadingText = 'Extracting PDF text page by page...',
  onFileSelected,
  onError,
  onClear,
  accentColor = 'cyan',
  disabled = false,
}) => {
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const dragCounter = useRef<number>(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropzoneRef = useRef<HTMLDivElement>(null);

  const isCyan = accentColor === 'cyan';
  const activeBorderClass = isCyan
    ? 'border-cyan-400 bg-cyan-950/30 ring-2 ring-cyan-500/20 scale-[1.008]'
    : 'border-blue-400 bg-blue-950/30 ring-2 ring-blue-500/20 scale-[1.008]';
  const iconColorClass = isCyan ? 'text-cyan-400' : 'text-blue-400';

  // Prevent default browser drag/drop behavior on window to prevent opening files in new tab
  useEffect(() => {
    const handleGlobalDragOver = (e: DragEvent) => {
      e.preventDefault();
    };
    const handleGlobalDrop = (e: DragEvent) => {
      e.preventDefault();
    };

    window.addEventListener('dragover', handleGlobalDragOver);
    window.addEventListener('drop', handleGlobalDrop);

    return () => {
      window.removeEventListener('dragover', handleGlobalDragOver);
      window.removeEventListener('drop', handleGlobalDrop);
    };
  }, []);

  const validateAndProcessFile = (file: File) => {
    // 1. Validate PDF format
    const isPdf =
      file.name.toLowerCase().endsWith('.pdf') ||
      file.type === 'application/pdf' ||
      file.type === 'application/x-pdf';

    if (!isPdf) {
      onError?.(`Unsupported file format "${file.name}". Only PDF documents (.pdf) are accepted.`);
      return;
    }

    // 2. Validate Size Limit
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      onError?.(
        `File "${file.name}" (${formatFileSize(file.size)}) exceeds the maximum allowed size of ${maxSizeMB}MB.`
      );
      return;
    }

    // 3. Clear errors and pass file to callback
    onFileSelected(file);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || isLoading) return;

    dragCounter.current += 1;
    setIsDragOver(true);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || isLoading) return;

    try {
      e.dataTransfer.dropEffect = 'copy';
    } catch {
      // Fallback for strict browser security policies
    }

    if (!isDragOver) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || isLoading) return;

    dragCounter.current -= 1;
    const currentTarget = e.currentTarget;
    const relatedTarget = e.relatedTarget as Node | null;

    // Only deactivate drag state if cursor completely leaves the dropzone container
    if (!relatedTarget || !currentTarget.contains(relatedTarget) || dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragOver(false);
    }
  };

  const handleDragEnd = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragOver(false);

    if (disabled || isLoading) return;

    let fileToProcess: File | null = null;

    // First try dataTransfer.files
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (e.dataTransfer.files.length > 1) {
        onError?.('Please drop exactly one PDF file at a time.');
        return;
      }
      fileToProcess = e.dataTransfer.files[0];
    } else if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      // Fallback to dataTransfer.items
      const item = e.dataTransfer.items[0];
      if (item.kind === 'file') {
        fileToProcess = item.getAsFile();
      }
    }

    if (!fileToProcess) {
      onError?.('No readable file was detected in the drop event.');
      return;
    }

    validateAndProcessFile(fileToProcess);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
      // Reset input value so re-selecting the exact same file triggers onChange
      e.target.value = '';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if ((e.key === 'Enter' || e.key === ' ') && !isLoading && !disabled) {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  const handleContainerClick = () => {
    if (!isLoading && !disabled && !currentFile) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div
      ref={dropzoneRef}
      role="region"
      aria-label={label}
      tabIndex={disabled || isLoading ? -1 : 0}
      onKeyDown={handleKeyDown}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDragEnd={handleDragEnd}
      onDrop={handleDrop}
      onClick={handleContainerClick}
      className={`border border-dashed rounded-2xl p-6 text-center transition-all duration-200 relative outline-none select-none ${
        isDragOver
          ? activeBorderClass
          : 'border-white/[0.12] hover:border-white/[0.24] bg-white/[0.02] hover:bg-white/[0.035] focus-visible:ring-2 focus-visible:ring-white/20'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <input
        ref={fileInputRef}
        type="file"
        id={id}
        accept={accept}
        className="hidden"
        disabled={disabled || isLoading}
        onChange={handleInputChange}
      />

      {/* Visual Drag-Over Overlay (renders with pointer-events-none so it doesn't cause fake dragleave) */}
      {isDragOver && (
        <div className="absolute inset-0 z-20 rounded-2xl flex flex-col items-center justify-center space-y-2 pointer-events-none bg-[#0c0d12]/95 border-2 border-dashed border-cyan-400 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="p-3.5 rounded-2xl bg-white/[0.08] border border-white/[0.15] text-white shadow-2xl mb-1">
            <UploadCloud className={`w-7 h-7 ${iconColorClass} animate-bounce`} />
          </div>
          <p className="text-sm font-semibold text-white tracking-tight">
            Drop PDF File Here
          </p>
          <p className="text-xs text-zinc-400">Release to start instant text extraction</p>
        </div>
      )}

      {isLoading ? (
        <div className="py-8 flex flex-col items-center justify-center space-y-3 pointer-events-none">
          <div className="p-3 rounded-2xl bg-white/[0.04] border border-white/[0.08] shadow-inner">
            <Loader2 className={`w-6 h-6 ${iconColorClass} animate-spin`} />
          </div>
          <p className="text-xs font-medium text-zinc-300 tracking-tight">{loadingText}</p>
        </div>
      ) : currentFile ? (
        <div 
          className="flex flex-col items-center justify-center min-h-[140px] space-y-3.5"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-3.5 rounded-2xl bg-white/[0.04] border border-white/[0.08] text-zinc-400 shadow-inner">
            <FileText className={`w-7 h-7 ${iconColorClass}`} />
          </div>
          <div className="text-center max-w-full px-4">
            <p className="text-sm font-semibold text-zinc-100 truncate max-w-xs sm:max-w-md mx-auto tracking-tight" title={currentFile.name}>
              {currentFile.name}
            </p>
            <div className="flex items-center justify-center space-x-2 mt-1">
              <span className="text-[11px] font-mono text-zinc-400 px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.06]">
                {formatFileSize(currentFile.size)}
              </span>
              <span className="text-[11px] text-zinc-500 font-medium">• PDF Document</span>
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 rounded-xl text-xs font-medium text-zinc-200 hover:text-white bg-white/[0.06] hover:bg-white/[0.12] border border-white/[0.1] transition-all shadow-sm inline-flex items-center cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1.5 text-zinc-400" />
              Change PDF
            </button>

            {onClear && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onClear();
                }}
                className="px-3 py-1.5 rounded-xl text-xs font-medium text-rose-300 hover:text-rose-200 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 transition-all inline-flex items-center cursor-pointer"
              >
                <X className="w-3.5 h-3.5 mr-1 text-rose-400" />
                Remove
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center min-h-[140px] space-y-2 pointer-events-none">
          <div className="p-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.08] text-zinc-400 mb-1 shadow-inner group-hover:border-white/[0.16] transition-colors">
            <UploadCloud className={`w-7 h-7 ${iconColorClass}`} />
          </div>
          <div>
            <p className="text-sm font-semibold text-zinc-200 tracking-tight">
              {label}
            </p>
            <p className="text-xs text-zinc-500 mt-0.5">
              {sublabel}
            </p>
          </div>
          <div className="pt-2">
            <button
              type="button"
              className="pointer-events-auto px-4 py-2 rounded-xl text-xs font-medium text-white bg-white/[0.08] hover:bg-white/[0.14] border border-white/[0.12] transition-all shadow-sm cursor-pointer hover:scale-[1.02]"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              Select PDF File
            </button>
          </div>
        </div>
      )}
    </div>
  );
};


