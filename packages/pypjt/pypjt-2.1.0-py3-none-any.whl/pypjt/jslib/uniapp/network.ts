export type HttpMethod =
  | "GET"
  | "POST"
  | "PUT"
  | "DELETE"
  | "CONNECT"
  | "HEAD"
  | "OPTIONS"
  | "TRACE";

export type ResponseType = "text" | "arraybuffer";

export type DataType = "json" | string;

export interface UniRequestSuccessResult {
  data: unknown;
  statusCode: number;
  header: Record<string, string>;
  cookies?: string[];
}

export interface UniRequestFailResult {
  errMsg: string;
}

export interface UniRequestOptions {
  url: string;
  data?: string | ArrayBuffer | AnyObject | undefined;
  header?: Record<string, string>;
  method?: HttpMethod;
  timeout?: number;
  dataType?: DataType;
  responseType?: ResponseType;
  sslVerify?: boolean;
  withCredentials?: boolean;
  firstIpv4?: boolean;
  enableHttp2?: boolean;
  enableQuic?: boolean;
  enableCache?: boolean;
  enableHttpDNS?: boolean;
  httpDNSServiceId?: string;
  enableChunked?: boolean;
  forceCellularNetwork?: boolean;
  enableCookie?: boolean;
  cloudCache?: object | boolean;
  defer?: boolean;
  success?: (result: UniRequestSuccessResult) => void;
  fail?: (result: UniRequestFailResult) => void;
  complete?: () => void;
}

export interface RequestTask {
  abort(): void;
  onHeadersReceived?: (
    callback: (result: {
      header: Record<string, string>;
      statusCode: number;
      cookies?: string[];
    }) => void,
  ) => void;
  offHeadersReceived?: (callback?: () => void) => void;
  onChunkReceived?: (callback: (result: { data: ArrayBuffer }) => void) => void;
  offChunkReceived?: (callback?: () => void) => void;
}

export function request<T = unknown>(
  url: string,
  method: HttpMethod,
  data?: string | ArrayBuffer | AnyObject | undefined,
  header?: Record<string, string>,
  options: Partial<UniRequestOptions> = {},
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    uni.request({
      url,
      method,
      data,
      header,
      ...options,
      success(res: UniRequestSuccessResult) {
        const isSuccess = res.statusCode >= 200 && res.statusCode < 300;
        if (!isSuccess) {
          reject(new Error(JSON.stringify(res)));
          return;
        }
        resolve(res.data as T);
      },
      fail(err: UniRequestFailResult) {
        reject(new Error(err.errMsg || "Network request failed"));
      },
    });
  });
}

export function get<T = unknown>(
  url: string,
  params?: AnyObject,
  header?: Record<string, string>,
  options?: Partial<UniRequestOptions>,
): Promise<T> {
  return request<T>(url, "GET", params, header, options);
}

export function post<T = unknown>(
  url: string,
  data?: string | ArrayBuffer | AnyObject,
  header?: Record<string, string>,
  options?: Partial<UniRequestOptions>,
): Promise<T> {
  return request<T>(url, "POST", data, header, options);
}
