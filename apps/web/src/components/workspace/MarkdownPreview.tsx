import ReactMarkdown from "react-markdown";

// Renders artifact Markdown. Pure presentational.
export function MarkdownPreview({ content }: { content: string }) {
  return (
    <div
      className={
        "max-w-[760px] px-10 py-6 text-[14.5px] leading-7 text-text-body " +
        "[&_h1]:mb-1 [&_h1]:text-2xl [&_h1]:font-semibold [&_h1]:text-text " +
        "[&_h2]:mb-1 [&_h2]:mt-5 [&_h2]:text-[15px] [&_h2]:font-semibold [&_h2]:text-text " +
        "[&_p]:my-2 [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5 [&_li]:my-1 " +
        "[&_code]:rounded [&_code]:bg-sunken [&_code]:px-1 [&_code]:font-mono [&_code]:text-[12.5px]"
      }
    >
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
